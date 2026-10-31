package com.howtodoinjava.guardrails.orderdesk;

import java.math.BigDecimal;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;

/**
 * The three OrderDesk tools. They contain no security checks on purpose:
 * the checks live in the guard layer, outside the tools.
 */
public class OrderDeskTools {

    private final OrderStore store;
    private final Map<String, AtomicInteger> executions = new ConcurrentHashMap<>();

    public OrderDeskTools(OrderStore store) {
        this.store = store;
    }

    @Tool(description = "Look up an order by its id. Returns the customer, the total and the order note.")
    public String lookupOrder(@ToolParam(description = "Order id, for example A-1001") String orderId) {
        count("lookupOrder");
        return store.find(orderId)
                .map(o -> "Order " + o.orderId() + ", customer " + o.customerId() + ", total " + o.total()
                        + " USD, note: " + o.note())
                .orElse("No order " + orderId);
    }

    @Tool(description = "Refund an amount in USD for an order.")
    public String issueRefund(@ToolParam(description = "Order id") String orderId,
                              @ToolParam(description = "Amount in USD") BigDecimal amount,
                              @ToolParam(description = "Short reason for the refund") String reason) {
        count("issueRefund");
        store.recordRefund(new OrderStore.Refund(orderId, amount, reason));
        return "Refunded " + amount + " USD for order " + orderId;
    }

    @Tool(description = "Delete a customer and all their data.")
    public String deleteCustomer(@ToolParam(description = "Customer id") String customerId) {
        count("deleteCustomer");
        return store.deleteCustomer(customerId) ? "Deleted " + customerId : "No customer " + customerId;
    }

    private void count(String tool) {
        executions.computeIfAbsent(tool, t -> new AtomicInteger()).incrementAndGet();
    }

    /** How often a tool body really ran. The attack tests assert on this. */
    public int executions(String tool) {
        AtomicInteger count = executions.get(tool);
        return count == null ? 0 : count.get();
    }
}
