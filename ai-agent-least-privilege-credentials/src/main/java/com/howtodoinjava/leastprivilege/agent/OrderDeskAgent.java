package com.howtodoinjava.leastprivilege.agent;

import java.util.Map;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.ToolCallingAdvisor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.model.tool.ToolCallingManager;
import org.springframework.ai.tool.execution.ToolExecutionExceptionProcessor;

import com.howtodoinjava.leastprivilege.tools.OrderDeskTools;

/** The OrderDesk agent: one model, three tools, and the signed-in user passed outside the prompt. */
public class OrderDeskAgent {

    public record Session(String customerId, String accessToken) {
    }

    public static final String SYSTEM_PROMPT = """
            You are OrderDesk, a support assistant for an online coffee equipment shop.
            Use the tools to list and cancel the signed-in customer's orders.
            Answer in one or two short sentences.""";

    private final ChatClient chatClient;
    private final OrderDeskTools tools;

    public OrderDeskAgent(ChatModel model, OrderDeskTools tools, ToolExecutionExceptionProcessor errors,
                          String systemPrompt) {
        ToolCallingManager toolCallingManager = ToolCallingManager.builder()
                .toolExecutionExceptionProcessor(errors)
                .build();
        this.chatClient = ChatClient.builder(model)
                .defaultSystem(systemPrompt)
                .defaultAdvisors(ToolCallingAdvisor.builder().toolCallingManager(toolCallingManager).build())
                .build();
        this.tools = tools;
    }

    public String chat(Session session, String message) {
        return chatClient.prompt()
                .user(message)
                .tools(tools)
                .toolContext(Map.of(
                        "customerId", session.customerId(),
                        "userAccessToken", session.accessToken()))
                .call()
                .content();
    }
}
