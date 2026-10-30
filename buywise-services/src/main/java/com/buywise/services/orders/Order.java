package com.buywise.services.orders;

import com.fasterxml.jackson.annotation.JsonRawValue;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public record Order(String orderId, String customerId, LocalDateTime placedAt, String status,
                    @JsonRawValue String fulfilment, BigDecimal subtotal, BigDecimal shippingFee, BigDecimal tax,
                    BigDecimal total, @JsonRawValue String payment, String trackingNumber,
                    LocalDateTime pickupHoldUntil, List<OrderItem> items) {

    Order withItems(List<OrderItem> items) {
        return new Order(orderId, customerId, placedAt, status, fulfilment, subtotal, shippingFee, tax, total,
                payment, trackingNumber, pickupHoldUntil, items);
    }
}
