package com.howtodoinjava.sandbox;

import org.junit.jupiter.api.Test;
import org.springframework.ai.support.ToolCallbacks;
import org.springframework.ai.tool.ToolCallback;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;

class OrderDeskToolsTest {

    static final String ORDERS = """
            [{"id":"A-1001","status":"OPEN","total":120.50},
             {"id":"A-1003","status":"OPEN","total":42.25}]""";

    @Test
    void springAiCallsTheToolThroughTheSandbox() {
        ToolCallback[] callbacks = ToolCallbacks.from(
                new OrderDeskTools(new ConstrainedSandbox(1_000_000, Duration.ofSeconds(2)), ORDERS));
        ToolCallback tool = callbacks[0];

        String sum = tool.call("{\"code\": \"orders.reduce((s, o) => s + o.total, 0)\"}");
        String secret = tool.call("{\"code\": \"Java.type('java.lang.System').getenv('DB_PASSWORD')\"}");

        assertThat(tool.getToolDefinition().name()).isEqualTo("runJavaScript");
        assertThat(sum).isEqualTo("162.75");
        assertThat(secret).contains("Code failed (ERROR): ReferenceError: Java is not defined")
                .doesNotContain(AttackTestSupport.ENV_SECRET);
    }
}
