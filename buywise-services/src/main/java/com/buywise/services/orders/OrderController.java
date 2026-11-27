package com.buywise.services.orders;

import com.buywise.services.shared.CurrentCustomer;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * The customer comes from the validated token's customer_id claim (ADR-050) - never from a header, the request body
 * or an AI tool argument. Scope and role per endpoint are checked in shared.SecurityConfig.
 */
@RestController
@RequestMapping("/api/orders")
class OrderController {

    private final OrderService orders;

    OrderController(OrderService orders) {
        this.orders = orders;
    }

    @GetMapping
    List<Order> orders(@AuthenticationPrincipal Jwt token, @RequestParam(defaultValue = "5") int limit) {
        return orders.orders(CurrentCustomer.id(token), Math.min(limit, 20));
    }

    @GetMapping("/{orderId}")
    Order order(@AuthenticationPrincipal Jwt token, @PathVariable String orderId) {
        return orders.order(orderId.toUpperCase(), CurrentCustomer.id(token))
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown order " + orderId));
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    Order place(@AuthenticationPrincipal Jwt token, @Valid @RequestBody PlaceOrder request) {
        return orders.place(CurrentCustomer.id(token), request);
    }

    @PostMapping("/quote")
    Order quote(@AuthenticationPrincipal Jwt token, @Valid @RequestBody PlaceOrder request) {
        return orders.quote(CurrentCustomer.id(token), request);
    }

    @PostMapping("/{orderId}/cancel")
    Order cancel(@AuthenticationPrincipal Jwt token, @PathVariable String orderId) {
        return orders.cancel(orderId.toUpperCase(), CurrentCustomer.id(token));
    }
}
