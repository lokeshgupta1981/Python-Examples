package com.howtodoinjava.guardrails.guard;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Approvals bound to one exact call: the approval stores the SHA-256 fingerprint of
 * user, tool and arguments, and only a call with the same fingerprint can use it, once.
 */
public class ApprovalService {

    public enum Status { PENDING, APPROVED, USED }

    public record Approval(String id, String requestedBy, String tool, String fingerprint, String summary,
                           Status status, String approvedBy) {

        Approval with(Status newStatus, String approver) {
            return new Approval(id, requestedBy, tool, fingerprint, summary, newStatus, approver);
        }
    }

    private final Map<String, Approval> approvals = new ConcurrentHashMap<>();
    private final AtomicInteger sequence = new AtomicInteger();

    /** Creates a pending approval, or returns the open one for the same exact call. */
    public Approval request(ToolCall call) {
        String fingerprint = call.fingerprint();
        return approvals.values().stream()
                .filter(a -> a.fingerprint().equals(fingerprint) && a.status() != Status.USED)
                .findFirst()
                .orElseGet(() -> {
                    String id = "APR-" + sequence.incrementAndGet();
                    Approval approval = new Approval(id, call.user(), call.tool(), fingerprint,
                            call.tool() + " " + call.args(), Status.PENDING, null);
                    approvals.put(id, approval);
                    return approval;
                });
    }

    /** Called from the approval endpoint, never from a tool. */
    public Approval approve(String approvalId, String approver, String approverRole) {
        Approval approval = approvals.get(approvalId);
        if (approval == null || approval.status() != Status.PENDING) {
            throw new IllegalStateException("No pending approval " + approvalId);
        }
        if (!approverRole.equals("supervisor") || approver.equals(approval.requestedBy())) {
            throw new IllegalStateException(approver + " may not approve " + approvalId);
        }
        Approval approved = approval.with(Status.APPROVED, approver);
        approvals.put(approvalId, approved);
        return approved;
    }

    public boolean isApproved(ToolCall call) {
        return findApproved(call).isPresent();
    }

    /** Marks the approval for this exact call as used, so it can't run twice. */
    public void consume(ToolCall call) {
        findApproved(call).ifPresent(a -> approvals.put(a.id(), a.with(Status.USED, a.approvedBy())));
    }

    public Optional<Approval> find(String approvalId) {
        return Optional.ofNullable(approvals.get(approvalId));
    }

    private Optional<Approval> findApproved(ToolCall call) {
        String fingerprint = call.fingerprint();
        return approvals.values().stream()
                .filter(a -> a.status() == Status.APPROVED && a.fingerprint().equals(fingerprint))
                .findFirst();
    }
}
