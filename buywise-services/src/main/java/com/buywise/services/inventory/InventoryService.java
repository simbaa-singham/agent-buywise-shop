package com.buywise.services.inventory;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;

/** Inventory module API: stores (stock locations) and stock per SKU and store. */
@Service
public class InventoryService {

    private static final String STORE_SQL = """
            SELECT store_id, name, address, city, state, zip, timezone, sales_tax_rate, hours::text AS hours
            FROM inventory.stores""";

    private final JdbcClient jdbc;

    InventoryService(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public List<Store> stores() {
        return jdbc.sql(STORE_SQL + " ORDER BY name").query(Store.class).list();
    }

    public Optional<Store> store(String storeId) {
        return jdbc.sql(STORE_SQL + " WHERE store_id = ?").param(storeId).query(Store.class).optional();
    }

    /** Stock for the given SKUs, at one store or (storeId null) at every store. */
    public List<StockLevel> stock(Collection<String> skus, String storeId) {
        if (skus.isEmpty()) return List.of();
        return jdbc.sql("""
                        SELECT s.sku, s.store_id, st.name AS store_name, s.quantity
                        FROM inventory.stock s JOIN inventory.stores st USING (store_id)
                        WHERE s.sku IN (:skus) AND (CAST(:storeId AS text) IS NULL OR s.store_id = :storeId)
                        ORDER BY s.sku, st.name""")
                .param("skus", skus).param("storeId", storeId)
                .query(StockLevel.class).list();
    }

    /** Takes units off the shelf for a pickup order; false if the store does not have enough. */
    public boolean reserve(String storeId, String sku, int quantity) {
        return jdbc.sql("UPDATE inventory.stock SET quantity = quantity - ? WHERE store_id = ? AND sku = ? AND quantity >= ?")
                .params(quantity, storeId, sku, quantity).update() == 1;
    }

    public void release(String storeId, String sku, int quantity) {
        jdbc.sql("UPDATE inventory.stock SET quantity = quantity + ? WHERE store_id = ? AND sku = ?")
                .params(quantity, storeId, sku).update();
    }
}
