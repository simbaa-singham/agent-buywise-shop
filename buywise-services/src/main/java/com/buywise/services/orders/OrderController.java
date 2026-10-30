package com.buywise.services.orders;

import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * The customer comes from the X-Customer-Id header set by the caller (MCP server) from the logged-in session,
 * never from the request body or an AI tool argument (simplified stand-in for token exchange, ADR-028).
 */
@RestController
@RequestMapping("/api/orders")
class OrderController {

    private static final String CUSTOMER = "X-Customer-Id";
    private final OrderService orders;

    OrderController(OrderService orders) {
        this.orders = orders;
    }

    @GetMapping
    List<Order> orders(@RequestHeader(CUSTOMER) String customerId, @RequestParam(defaultValue = "5") int limit) {
        return orders.orders(customerId, Math.min(limit, 20));
    }

    @GetMapping("/{orderId}")
    Order order(@RequestHeader(CUSTOMER) String customerId, @PathVariable String orderId) {
        return orders.order(orderId.toUpperCase(), customerId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown order " + orderId));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    Order place(@RequestHeader(CUSTOMER) String customerId, @Valid @RequestBody PlaceOrder request) {
        return orders.place(customerId, request);
    }

    @PostMapping("/quote")
    Order quote(@RequestHeader(CUSTOMER) String customerId, @Valid @RequestBody PlaceOrder request) {
        return orders.quote(customerId, request);
    }

    @PostMapping("/{orderId}/cancel")
    Order cancel(@RequestHeader(CUSTOMER) String customerId, @PathVariable String orderId) {
        return orders.cancel(orderId.toUpperCase(), customerId);
    }
}
