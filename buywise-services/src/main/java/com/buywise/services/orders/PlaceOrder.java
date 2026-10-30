package com.buywise.services.orders;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Pattern;
import java.util.List;

/** Delivery goes to the customer's saved address; pickup needs a store. Payment is mocked (no card data). */
public record PlaceOrder(@NotEmpty List<@Valid Line> items,
                         @NotBlank @Pattern(regexp = "pickup|delivery") String fulfilment,
                         String storeId) {

    public record Line(@NotBlank String sku, @Min(1) @Max(5) int quantity) {}
}
