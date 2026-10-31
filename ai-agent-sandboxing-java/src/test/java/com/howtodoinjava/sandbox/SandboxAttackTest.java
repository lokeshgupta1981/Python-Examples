package com.howtodoinjava.sandbox;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.EnumSource;
import org.junit.jupiter.params.provider.MethodSource;

import java.time.Duration;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;

import static com.howtodoinjava.sandbox.ExecutionResult.Status.LIMIT_EXCEEDED;
import static com.howtodoinjava.sandbox.ExecutionResult.Status.TIMED_OUT;
import static org.assertj.core.api.Assertions.assertThat;

class SandboxAttackTest {

    static AttackTestSupport targets;

    static final List<CodeSandbox> SANDBOXES = List.of(
            new ConstrainedSandbox(1_000_000, Duration.ofSeconds(2)),
            new UntrustedSandbox());

    @BeforeAll
    static void setUp() throws Exception {
        targets = new AttackTestSupport();
    }

    @AfterAll
    static void tearDown() throws Exception {
        targets.close();
    }

    static Stream<Arguments> everyAttackOnEverySandbox() {
        return SANDBOXES.stream().flatMap(sandbox ->
                Arrays.stream(Attack.values()).map(attack -> Arguments.of(sandbox, attack)));
    }

    @ParameterizedTest(name = "{0} blocks {1}")
    @MethodSource("everyAttackOnEverySandbox")
    void sandboxBlocksAttack(CodeSandbox sandbox, Attack attack) {
        ExecutionResult result = sandbox.run(targets.codeFor(attack));

        assertThat(result.succeeded()).isFalse();
        assertThat(result.output())
                .doesNotContain(AttackTestSupport.ENV_SECRET)
                .doesNotContain(AttackTestSupport.FILE_SECRET);
        if (attack == Attack.INFINITE_LOOP || attack == Attack.MEMORY_BOMB) {
            assertThat(result.status()).isIn(LIMIT_EXCEEDED, TIMED_OUT);
        }
    }

    @ParameterizedTest(name = "unsafe executor allows {0}")
    @EnumSource(value = Attack.class, names = {"READ_SECRET_ENV", "READ_FILE", "OPEN_SOCKET", "RUN_PROCESS"})
    void unsafeExecutorAllowsAttack(Attack attack) {
        ExecutionResult result = new UnsafeExecutor().run(targets.codeFor(attack));

        assertThat(result.succeeded()).isTrue();
        assertThat(result.output()).isIn(
                AttackTestSupport.ENV_SECRET, "db.password=" + AttackTestSupport.FILE_SECRET,
                "connected", "process ran");
    }

    @Test
    void sandboxStillRunsLegitimateCode() {
        String orders = """
                [{"id":"A-1001","status":"OPEN","total":120.50},
                 {"id":"A-1002","status":"SHIPPED","total":75.00},
                 {"id":"A-1003","status":"OPEN","total":42.25}]""";
        String code = "orders.filter(o => o.status === 'OPEN').reduce((sum, o) => sum + o.total, 0)";

        for (CodeSandbox sandbox : SANDBOXES) {
            assertThat(new OrderDeskCodeTool(sandbox, orders).runJavaScript(code)).isEqualTo("162.75");
        }
    }
}
