package com.howtodoinjava.guardrails.guard;

import java.math.BigDecimal;
import java.util.Optional;

import com.howtodoinjava.guardrails.orderdesk.Order;
import com.howtodoinjava.guardrails.orderdesk.OrderStore;

/**
 * Business checks on the arguments: the order exists, belongs to the customer
 * on this conversation, and a refund is above zero and not above the order total.
 */
public class RefundArguments implements Gate {

    private final OrderStore store;

    public RefundArguments(OrderStore store) {
        this.store = store;
    }

    @Override
    public Decision check(ToolCall call) {
        if (!call.args().containsKey("orderId")) {
            return Decision.allow();
        }
        Optional<Order> order = store.find(call.text("orderId"));
        if (order.isEmpty() || !order.get().customerId().equals(call.customerId())) {
            return Decision.deny("arguments", "order " + call.text("orderId")
                    + " does not belong to customer " + call.customerId());
        }
        if (!call.tool().equals("issueRefund")) {
            return Decision.allow();
        }
        BigDecimal amount;
        try {
            amount = call.decimal("amount");
        } catch (IllegalArgumentException e) {
            return Decision.deny("arguments", e.getMessage());
        }
        if (amount.signum() <= 0 || amount.scale() > 2) {
            return Decision.deny("arguments", "amount must be a positive USD amount, got " + amount);
        }
        if (amount.compareTo(order.get().total()) > 0) {
            return Decision.deny("arguments", "amount " + amount + " is above the order total "
                    + order.get().total());
        }
        return Decision.allow();
    }
}
