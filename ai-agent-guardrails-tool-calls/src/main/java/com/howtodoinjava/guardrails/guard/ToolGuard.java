package com.howtodoinjava.guardrails.guard;

import java.util.List;

/**
 * Runs the gates in order. The first gate that doesn't allow the call decides;
 * every decision is written to the audit log.
 */
public class ToolGuard {

    private final List<Gate> gates;
    private final AuditLog audit;

    public ToolGuard(List<Gate> gates, AuditLog audit) {
        this.gates = List.copyOf(gates);
        this.audit = audit;
    }

    public Decision evaluate(ToolCall call) {
        for (Gate gate : gates) {
            Decision decision;
            try {
                decision = gate.check(call);
            } catch (RuntimeException e) {
                decision = Decision.deny(gate.getClass().getSimpleName(), "check failed, denying by default");
            }
            if (!decision.allowed()) {
                audit.record(call, decision);
                return decision;
            }
        }
        gates.forEach(gate -> gate.onAllowed(call));
        Decision allowed = Decision.allow();
        audit.record(call, allowed);
        return allowed;
    }
}
