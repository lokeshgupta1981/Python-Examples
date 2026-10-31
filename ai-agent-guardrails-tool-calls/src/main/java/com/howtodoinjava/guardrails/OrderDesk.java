package com.howtodoinjava.guardrails;

import java.math.BigDecimal;
import java.time.Clock;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.howtodoinjava.guardrails.guard.ApprovalService;
import com.howtodoinjava.guardrails.guard.AuditLog;
import com.howtodoinjava.guardrails.guard.CedarRefundPolicy;
import com.howtodoinjava.guardrails.guard.RefundArguments;
import com.howtodoinjava.guardrails.guard.RoleAllowList;
import com.howtodoinjava.guardrails.guard.SpendLimit;
import com.howtodoinjava.guardrails.guard.ToolGuard;
import com.howtodoinjava.guardrails.orderdesk.OrderDeskTools;
import com.howtodoinjava.guardrails.orderdesk.OrderStore;

/**
 * Wires the OrderDesk example: data, tools, and the guard with its gates in order.
 */
public class OrderDesk {

    public final OrderStore store = OrderStore.withSampleData();
    public final OrderDeskTools tools = new OrderDeskTools(store);
    public final ApprovalService approvals = new ApprovalService();
    public final AuditLog audit;
    public final RoleAllowList allowList = new RoleAllowList(Map.of(
            "support", Set.of("lookupOrder", "issueRefund"),
            "supervisor", Set.of("lookupOrder", "issueRefund")));
    public final SpendLimit spendLimit;
    public final ToolGuard guard;

    public OrderDesk(Clock clock, boolean printAudit) {
        this.audit = new AuditLog(clock, printAudit);
        this.spendLimit = new SpendLimit(new BigDecimal("500.00"), clock);
        this.guard = new ToolGuard(List.of(
                allowList,
                new RefundArguments(store),
                CedarRefundPolicy.fromClasspath("orderdesk.cedar", approvals),
                spendLimit),
                audit);
    }
}
