package com.buywise.services.inventory;

import com.fasterxml.jackson.annotation.JsonRawValue;
import java.math.BigDecimal;

public record Store(String storeId, String name, String address, String city, String state, String zip,
                    String timezone, BigDecimal salesTaxRate, @JsonRawValue String hours) {}
