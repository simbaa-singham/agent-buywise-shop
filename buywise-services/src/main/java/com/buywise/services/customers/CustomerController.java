package com.buywise.services.customers;

import com.buywise.services.shared.CurrentCustomer;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** The logged-in customer's own record only (ADR-050): looked up by the token's customer_id, never by a path id or
 * an email (both let any caller read any customer before). */
@RestController
@RequestMapping("/api/customers")
class CustomerController {

    private final CustomerService customers;

    CustomerController(CustomerService customers) {
        this.customers = customers;
    }

    @GetMapping("/me")
    Customer me(@AuthenticationPrincipal Jwt token) {
        String id = CurrentCustomer.id(token);
        return customers.customer(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown customer " + id));
    }
}
