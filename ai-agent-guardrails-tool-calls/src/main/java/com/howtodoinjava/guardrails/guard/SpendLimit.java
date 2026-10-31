package com.howtodoinjava.guardrails.guard;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.LocalDate;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A daily refund budget per user. The amount is counted only when the call
 * passed every gate, so denied and pending calls don't use the budget.
 */
public class SpendLimit implements Gate {

    private final BigDecimal dailyLimit;
    private final Clock clock;
    private final Map<String, BigDecimal> spent = new ConcurrentHashMap<>();

    public SpendLimit(BigDecimal dailyLimit, Clock clock) {
        this.dailyLimit = dailyLimit;
        this.clock = clock;
    }

    @Override
    public Decision check(ToolCall call) {
        if (!call.tool().equals("issueRefund")) {
            return Decision.allow();
        }
        BigDecimal after = spentToday(call.user()).add(call.decimal("amount"));
        if (after.compareTo(dailyLimit) > 0) {
            return Decision.deny("spend-limit", "daily refund limit of " + dailyLimit + " USD reached for "
                    + call.user() + " (already refunded " + spentToday(call.user()) + ")");
        }
        return Decision.allow();
    }

    @Override
    public void onAllowed(ToolCall call) {
        if (call.tool().equals("issueRefund")) {
            spent.merge(key(call.user()), call.decimal("amount"), BigDecimal::add);
        }
    }

    public BigDecimal spentToday(String user) {
        return spent.getOrDefault(key(user), BigDecimal.ZERO);
    }

    private String key(String user) {
        return user + "|" + LocalDate.now(clock);
    }
}
