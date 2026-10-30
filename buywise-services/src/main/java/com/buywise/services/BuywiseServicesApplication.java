package com.buywise.services;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** Modular monolith (ADR-014): catalog, inventory, customers, orders - one package per module. */
@SpringBootApplication
public class BuywiseServicesApplication {
    public static void main(String[] args) {
        SpringApplication.run(BuywiseServicesApplication.class, args);
    }
}
