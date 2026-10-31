package com.howtodoinjava.guardrails.guard;

import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * One line per tool call decision. In production this goes to a log or an audit table.
 */
public class AuditLog {

    private final Clock clock;
    private final boolean print;
    private final List<String> lines = new CopyOnWriteArrayList<>();

    public AuditLog(Clock clock, boolean print) {
        this.clock = clock;
        this.print = print;
    }

    public void record(ToolCall call, Decision decision) {
        String line = Instant.now(clock).truncatedTo(ChronoUnit.SECONDS)
                + " user=" + call.user()
                + " role=" + call.role()
                + " tool=" + call.tool()
                + " args=sha256:" + call.fingerprint().substring(0, 12)
                + " decision=" + decision.outcome()
                + " gate=" + decision.gate()
                + (decision.approvalId() != null ? " approval=" + decision.approvalId() : "")
                + " reason=\"" + decision.reason() + "\"";
        lines.add(line);
        if (print) {
            System.out.println("AUDIT " + line);
        }
    }

    public List<String> lines() {
        return new ArrayList<>(lines);
    }
}
