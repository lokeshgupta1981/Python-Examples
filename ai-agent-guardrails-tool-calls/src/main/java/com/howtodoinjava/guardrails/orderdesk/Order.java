package com.howtodoinjava.guardrails.orderdesk;

import java.math.BigDecimal;

public record Order(String orderId, String customerId, BigDecimal total, String note) {
}
