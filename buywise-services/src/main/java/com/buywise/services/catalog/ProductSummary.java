package com.buywise.services.catalog;

import java.math.BigDecimal;
import java.time.LocalDate;

public record ProductSummary(String productId, String category, String family, String model,
                             String availability, LocalDate releaseDate, BigDecimal fromPrice) {}
