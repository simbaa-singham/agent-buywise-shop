package com.buywise.services.customers;

import java.util.Optional;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;

/** Customers module API. */
@Service
public class CustomerService {

    private static final String SQL = """
            SELECT customer_id, first_name, last_name, email, phone, address::text AS address, is_guest
            FROM customers.customers""";

    private final JdbcClient jdbc;

    CustomerService(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public Optional<Customer> customer(String customerId) {
        return jdbc.sql(SQL + " WHERE customer_id = ?").param(customerId).query(Customer.class).optional();
    }

    public Optional<Customer> byEmail(String email) {
        return jdbc.sql(SQL + " WHERE lower(email) = lower(?)").param(email).query(Customer.class).optional();
    }
}
