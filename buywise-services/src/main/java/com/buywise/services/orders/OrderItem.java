package com.buywise.services.orders;

import java.math.BigDecimal;

public record OrderItem(String sku, String productId, String model, int quantity, BigDecimal unitPrice) {}
