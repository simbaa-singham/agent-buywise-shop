package com.buywise.services.orders;

import com.buywise.services.catalog.CatalogService;
import com.buywise.services.catalog.Variant;
import com.buywise.services.customers.Customer;
import com.buywise.services.customers.CustomerService;
import com.buywise.services.inventory.InventoryService;
import com.buywise.services.inventory.Store;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

/** Orders module: place, look up and cancel orders. Prices always come from the catalog, never the caller. */
@Service
public class OrderService {

    private static final String ORDER_SQL = """
            SELECT order_id, customer_id, placed_at, status, fulfilment::text AS fulfilment, subtotal, shipping_fee,
                   tax, total, payment::text AS payment, tracking_number, pickup_hold_until, NULL AS items
            FROM orders.orders""";
    private static final List<String> CANCELLABLE = List.of("placed", "processing", "ready_for_pickup");

    private final JdbcClient jdbc;
    private final CatalogService catalog;
    private final InventoryService inventory;
    private final CustomerService customers;

    OrderService(JdbcClient jdbc, CatalogService catalog, InventoryService inventory, CustomerService customers) {
        this.jdbc = jdbc;
        this.catalog = catalog;
        this.inventory = inventory;
        this.customers = customers;
    }

    public List<Order> orders(String customerId, int limit) {
        List<Order> orders = jdbc.sql(ORDER_SQL + " WHERE customer_id = ? ORDER BY placed_at DESC LIMIT ?")
                .params(customerId, limit).query(Order.class).list();
        return orders.stream().map(o -> o.withItems(items(o.orderId()))).toList();
    }

    /** Only the owner sees an order; anyone else gets "not found" (no hint that it exists). */
    public Optional<Order> order(String orderId, String customerId) {
        return jdbc.sql(ORDER_SQL + " WHERE order_id = ? AND customer_id = ?").params(orderId, customerId)
                .query(Order.class).optional().map(o -> o.withItems(items(o.orderId())));
    }

    /** Prices an order exactly as place() would, without saving it or touching stock. */
    @Transactional(readOnly = true)
    public Order quote(String customerId, PlaceOrder request) {
        return build(customerId, request, false);
    }

    @Transactional
    public Order place(String customerId, PlaceOrder request) {
        return build(customerId, request, true);
    }

    private Order build(String customerId, PlaceOrder request, boolean save) {
        Customer customer = customers.customer(customerId)
                .orElseThrow(() -> error(HttpStatus.NOT_FOUND, "Unknown customer"));
        Map<String, Variant> variants = catalog.variants(request.items().stream().map(PlaceOrder.Line::sku).toList());

        List<OrderItem> items = new ArrayList<>();
        for (PlaceOrder.Line line : request.items()) {
            Variant v = variants.get(line.sku());
            if (v == null) throw error(HttpStatus.BAD_REQUEST, "Unknown SKU " + line.sku());
            if ("discontinued".equals(v.availability())) throw error(HttpStatus.CONFLICT, v.model() + " is discontinued");
            items.add(new OrderItem(v.sku(), v.productId(), v.model(), line.quantity(), v.listPrice()));
        }
        BigDecimal subtotal = items.stream().map(i -> i.unitPrice().multiply(BigDecimal.valueOf(i.quantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        String fulfilmentJson;
        BigDecimal taxRate;
        LocalDateTime holdUntil = null;
        if ("pickup".equals(request.fulfilment())) {
            Store store = inventory.store(request.storeId() == null ? "" : request.storeId())
                    .orElseThrow(() -> error(HttpStatus.BAD_REQUEST, "Pickup needs a valid store"));
            for (OrderItem i : items) {
                if (!"available".equals(catalogAvailability(variants, i)))
                    throw error(HttpStatus.CONFLICT, i.model() + " cannot be picked up before release");
                boolean enough = save ? inventory.reserve(store.storeId(), i.sku(), i.quantity())
                        : inventory.stock(List.of(i.sku()), store.storeId()).stream().anyMatch(s -> s.quantity() >= i.quantity());
                if (!enough)
                    throw error(HttpStatus.CONFLICT, "Not enough stock of " + i.sku() + " at " + store.name());
            }
            fulfilmentJson = jdbc.sql("SELECT jsonb_build_object('type','pickup','store_id',?)::text")
                    .param(store.storeId()).query(String.class).single();
            taxRate = store.salesTaxRate();
            holdUntil = LocalDateTime.now().plusDays(5);
        } else {
            if (customer.address() == null) throw error(HttpStatus.BAD_REQUEST, "No delivery address on file");
            fulfilmentJson = jdbc.sql("SELECT jsonb_build_object('type','delivery','method','standard','address',CAST(? AS jsonb))::text")
                    .param(customer.address()).query(String.class).single();
            taxRate = jdbc.sql("SELECT rate FROM orders.sales_tax WHERE state = ?").param(customer.state())
                    .query(BigDecimal.class).optional().orElse(BigDecimal.ZERO);
        }
        BigDecimal tax = subtotal.multiply(taxRate).setScale(2, RoundingMode.HALF_UP);
        BigDecimal total = subtotal.add(tax);

        if (!save) {
            return new Order(null, customerId, LocalDateTime.now(), "quote", fulfilmentJson, subtotal, BigDecimal.ZERO,
                    tax, total, null, null, holdUntil, items);
        }
        String orderId = "BW-" + jdbc.sql("SELECT nextval('orders.order_number_seq')").query(Long.class).single();
        jdbc.sql("""
                        INSERT INTO orders.orders (order_id, customer_id, placed_at, status, fulfilment, subtotal,
                                                   shipping_fee, tax, total, payment, pickup_hold_until)
                        VALUES (?, ?, now(), 'placed', CAST(? AS jsonb), ?, 0, ?, ?,
                                '{"method":"card","state":"authorized"}'::jsonb, ?)""")
                .params(orderId, customerId, fulfilmentJson, subtotal, tax, total, holdUntil).update();
        int n = 1;
        for (OrderItem i : items) {
            jdbc.sql("INSERT INTO orders.order_items VALUES (?, ?, ?, ?, ?, ?, ?)")
                    .params(orderId, n++, i.sku(), i.productId(), i.model(), i.quantity(), i.unitPrice()).update();
        }
        return order(orderId, customerId).orElseThrow();
    }

    @Transactional
    public Order cancel(String orderId, String customerId) {
        Order order = order(orderId, customerId).orElseThrow(() -> error(HttpStatus.NOT_FOUND, "Unknown order " + orderId));
        if (!CANCELLABLE.contains(order.status()))
            throw error(HttpStatus.CONFLICT, "Order " + orderId + " is " + order.status() + " and can no longer be cancelled");
        String storeId = jdbc.sql("SELECT fulfilment->>'store_id' FROM orders.orders WHERE order_id = ?")
                .param(orderId).query(String.class).optional().orElse(null);
        if (storeId != null) order.items().forEach(i -> inventory.release(storeId, i.sku(), i.quantity()));
        jdbc.sql("UPDATE orders.orders SET status = 'cancelled', payment = jsonb_set(payment, '{state}', '\"released\"') WHERE order_id = ?")
                .param(orderId).update();
        return order(orderId, customerId).orElseThrow();
    }

    private List<OrderItem> items(String orderId) {
        return jdbc.sql("SELECT sku, product_id, model, quantity, unit_price FROM orders.order_items WHERE order_id = ? ORDER BY line_no")
                .param(orderId).query(OrderItem.class).list();
    }

    private static String catalogAvailability(Map<String, Variant> variants, OrderItem i) {
        return variants.get(i.sku()).availability();
    }

    private static ResponseStatusException error(HttpStatus status, String message) {
        return new ResponseStatusException(status, message);
    }
}
