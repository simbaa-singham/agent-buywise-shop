package com.buywise.services.catalog;

import com.fasterxml.jackson.annotation.JsonRawValue;
import java.time.LocalDate;
import java.util.List;

public record Product(String productId, String category, String family, String model, String availability,
                      LocalDate releaseDate, @JsonRawValue String specs, String compatibilityNote,
                      List<Variant> variants) {}
