package com.howtodoinjava.guardrails.guard;

/**
 * The outcome of a gate or of the whole guard.
 */
public record Decision(Outcome outcome, String gate, String reason, String approvalId) {

    public enum Outcome { ALLOW, DENY, PENDING_APPROVAL }

    public static Decision allow() {
        return new Decision(Outcome.ALLOW, "-", "all checks passed", null);
    }

    public static Decision deny(String gate, String reason) {
        return new Decision(Outcome.DENY, gate, reason, null);
    }

    public static Decision pending(String gate, String reason, String approvalId) {
        return new Decision(Outcome.PENDING_APPROVAL, gate, reason, approvalId);
    }

    public boolean allowed() {
        return outcome == Outcome.ALLOW;
    }

    /** The text the model receives instead of the tool result. */
    public String toModelText() {
        return switch (outcome) {
            case ALLOW -> "ALLOWED";
            case DENY -> "DENIED by " + gate + ": " + reason + ". Do not retry this call.";
            case PENDING_APPROVAL -> "PENDING_APPROVAL " + approvalId + ": " + reason
                    + ". Tell the user the request is waiting for a supervisor.";
        };
    }
}
