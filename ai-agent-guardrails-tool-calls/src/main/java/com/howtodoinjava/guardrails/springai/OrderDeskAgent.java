package com.howtodoinjava.guardrails.springai;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.ToolCallingAdvisor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.model.tool.ToolCallLimitBehavior;
import org.springframework.ai.model.tool.ToolCallingManager;
import org.springframework.ai.support.ToolCallbacks;
import org.springframework.ai.tool.ToolCallback;

import com.howtodoinjava.guardrails.guard.RoleAllowList;
import com.howtodoinjava.guardrails.guard.ToolGuard;
import com.howtodoinjava.guardrails.orderdesk.OrderDeskTools;

/**
 * The OrderDesk refund agent on Spring AI. The prompt-only variant shows every tool and relies on
 * the system prompt; the guarded variant filters tools per role and wraps each one in the guard.
 */
public class OrderDeskAgent {

    public record Session(String user, String role, String customerId) {
    }

    public static final String SYSTEM_PROMPT = """
            You are OrderDesk, an assistant for support agents handling refunds.
            Use the tools to look up orders and issue refunds.
            Never refund more than 100 USD. Never delete customers.
            Answer in one or two short sentences.""";

    private final ChatClient chatClient;
    private final List<ToolCallback> tools;
    private final RoleAllowList allowList;

    private OrderDeskAgent(ChatModel model, List<ToolCallback> tools, RoleAllowList allowList) {
        ToolCallingManager toolCallingManager = ToolCallingManager.builder()
                .maxCallsPerTool("issueRefund", 3)
                .onLimitExceeded(ToolCallLimitBehavior.RETURN_ERROR_RESPONSE)
                .build();
        this.chatClient = ChatClient.builder(model)
                .defaultSystem(SYSTEM_PROMPT)
                .defaultAdvisors(ToolCallingAdvisor.builder().toolCallingManager(toolCallingManager).build())
                .build();
        this.tools = tools;
        this.allowList = allowList;
    }

    /** Only the system prompt protects the tools. */
    public static OrderDeskAgent promptOnly(ChatModel model, OrderDeskTools orderDeskTools) {
        return new OrderDeskAgent(model, Arrays.asList(ToolCallbacks.from(orderDeskTools)), null);
    }

    /** Every tool is wrapped in the guard, and each role sees only its own tools. */
    public static OrderDeskAgent guarded(ChatModel model, OrderDeskTools orderDeskTools,
                                         ToolGuard guard, RoleAllowList allowList) {
        List<ToolCallback> guarded = Arrays.stream(ToolCallbacks.from(orderDeskTools))
                .<ToolCallback>map(tool -> new GuardedToolCallback(tool, guard))
                .toList();
        return new OrderDeskAgent(model, guarded, allowList);
    }

    public String chat(Session session, String message) {
        return chatClient.prompt()
                .user(message)
                .toolCallbacks(toolsFor(session.role()))
                .toolContext(Map.of(
                        "user", session.user(),
                        "role", session.role(),
                        "customerId", session.customerId()))
                .call()
                .content();
    }

    List<ToolCallback> toolsFor(String role) {
        if (allowList == null) {
            return tools;
        }
        Set<String> allowed = allowList.toolsFor(role);
        return tools.stream()
                .filter(tool -> allowed.contains(tool.getToolDefinition().name()))
                .toList();
    }
}
