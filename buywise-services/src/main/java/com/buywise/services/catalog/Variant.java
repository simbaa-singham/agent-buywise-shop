package com.buywise.services.catalog;

import java.math.BigDecimal;

public record Variant(String sku, String productId, String model, String availability,
                      Integer storageGb, String size, String color, BigDecimal listPrice) {}
