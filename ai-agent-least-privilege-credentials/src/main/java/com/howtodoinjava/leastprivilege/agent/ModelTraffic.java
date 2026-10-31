package com.howtodoinjava.leastprivilege.agent;

import java.util.List;

import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.ToolResponseMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.model.tool.ToolCallingChatOptions;

/** Flattens the prompts sent to a model into text, so we can search them for secrets. */
public final class ModelTraffic {

    public static String toText(List<Prompt> prompts) {
        StringBuilder text = new StringBuilder();
        for (Prompt prompt : prompts) {
            for (Message message : prompt.getInstructions()) {
                text.append(message.getMessageType()).append(": ").append(message.getText()).append('\n');
                if (message instanceof AssistantMessage assistant) {
                    assistant.getToolCalls().forEach(call ->
                            text.append("  call ").append(call.name()).append(call.arguments()).append('\n'));
                }
                if (message instanceof ToolResponseMessage tool) {
                    tool.getResponses().forEach(r ->
                            text.append("  result ").append(r.name()).append(": ").append(r.responseData()).append('\n'));
                }
            }
            if (prompt.getOptions() instanceof ToolCallingChatOptions options) {
                options.getToolCallbacks().forEach(t -> text.append("  tool ")
                        .append(t.getToolDefinition().name()).append(' ')
                        .append(t.getToolDefinition().description()).append(' ')
                        .append(t.getToolDefinition().inputSchema()).append('\n'));
            }
        }
        return text.toString();
    }

    private ModelTraffic() {
    }
}
