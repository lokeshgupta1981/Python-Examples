package com.howtodoinjava.guardrails.langchain4j;

import java.math.BigDecimal;

import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;

import com.howtodoinjava.guardrails.orderdesk.OrderDeskTools;

/**
 * The same three tools with LangChain4j annotations. They delegate to OrderDeskTools,
 * so the tests can count how often a tool body really ran.
 */
public class OrderDeskLc4jTools {

    private final OrderDeskTools tools;

    public OrderDeskLc4jTools(OrderDeskTools tools) {
        this.tools = tools;
    }

    @Tool("Look up an order by its id. Returns the customer, the total and the order note.")
    public String lookupOrder(@P("Order id, for example A-1001") String orderId) {
        return tools.lookupOrder(orderId);
    }

    @Tool("Refund an amount in USD for an order.")
    public String issueRefund(@P("Order id") String orderId, @P("Amount in USD") BigDecimal amount,
                              @P("Short reason for the refund") String reason) {
        return tools.issueRefund(orderId, amount, reason);
    }

    @Tool("Delete a customer and all their data.")
    public String deleteCustomer(@P("Customer id") String customerId) {
        return tools.deleteCustomer(customerId);
    }
}
