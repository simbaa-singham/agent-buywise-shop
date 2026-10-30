package com.buywise.services.customers;

import com.fasterxml.jackson.annotation.JsonRawValue;

public record Customer(String customerId, String firstName, String lastName, String email, String phone,
                       @JsonRawValue String address, boolean isGuest) {

    /** Two-letter state of the customer's address, or null. */
    public String state() {
        if (address == null) return null;
        var m = java.util.regex.Pattern.compile("\"state\"\\s*:\\s*\"([A-Z]{2})\"").matcher(address);
        return m.find() ? m.group(1) : null;
    }
}
