package com.buywise.services.customers;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/customers")
class CustomerController {

    private final CustomerService customers;

    CustomerController(CustomerService customers) {
        this.customers = customers;
    }

    @GetMapping("/{customerId}")
    Customer customer(@PathVariable String customerId) {
        return customers.customer(customerId).orElseThrow(() -> notFound(customerId));
    }

    @GetMapping
    Customer byEmail(@RequestParam String email) {
        return customers.byEmail(email).orElseThrow(() -> notFound(email));
    }

    private static ResponseStatusException notFound(String id) {
        return new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown customer " + id);
    }
}
