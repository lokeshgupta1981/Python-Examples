package com.howtodoinjava.guardrails;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.api.Test;

import com.howtodoinjava.guardrails.guard.ApprovalService;
import com.howtodoinjava.guardrails.guard.CedarRefundPolicy;
import com.howtodoinjava.guardrails.guard.Decision;
import com.howtodoinjava.guardrails.guard.ToolCall;

class CedarPolicyTest {

    CedarRefundPolicy policy = CedarRefundPolicy.fromClasspath("orderdesk.cedar", new ApprovalService());

    static ToolCall refund(String role, String amount) {
        return new ToolCall("sam", role, "C-42", "issueRefund", Map.of("orderId", "A-1003", "amount", amount));
    }

    @ParameterizedTest(name = "{0} refunds {1} USD -> {2}")
    @CsvSource({
            "support,    40,      ALLOW",
            "support,    100,     ALLOW",
            "support,    100.01,  PENDING_APPROVAL",
            "support,    1000,    PENDING_APPROVAL",
            "support,    1000.01, DENY",
            "support,    5000,    DENY",
            "supervisor, 1000,    ALLOW",
            "supervisor, 5000,    DENY",
            "guest,      10,      DENY"
    })
    void decidesByRoleAndAmount(String role, String amount, Decision.Outcome expected) {
        Decision decision = policy.check(refund(role, amount));
        System.out.println("CEDAR " + role + " " + amount + " -> " + decision.outcome() + " " + decision.reason());
        assertThat(decision.outcome()).isEqualTo(expected);
    }

    @Test
    void failsClosedWhenTheCheckCannotRun() {
        ToolCall broken = new ToolCall("sam", "support", "C-42", "issueRefund", Map.of("orderId", "A-1003"));

        Decision decision = policy.check(broken);

        assertThat(decision.outcome()).isEqualTo(Decision.Outcome.DENY);
        assertThat(decision.reason()).isEqualTo("policy check failed, denying by default");
    }
}
