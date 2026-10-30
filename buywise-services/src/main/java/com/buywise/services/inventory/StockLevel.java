package com.buywise.services.inventory;

public record StockLevel(String sku, String storeId, String storeName, int quantity) {}
