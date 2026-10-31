package com.howtodoinjava.leastprivilege;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.Generation;
import org.springframework.ai.chat.prompt.ChatOptions;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.model.tool.ToolCallingChatOptions;

import com.howtodoinjava.leastprivilege.agent.ModelTraffic;

/**
 * Plays a model that a prompt injection has already taken over: it asks for the
 * tool calls we script, in order, and records everything it is sent.
 */
class ScriptedChatModel implements ChatModel {

    private final Deque<AssistantMessage> replies = new ArrayDeque<>();
    private final List<Prompt> prompts = new ArrayList<>();
    private int ids;

    ScriptedChatModel thenCall(String tool, String json) {
        replies.add(AssistantMessage.builder().content("")
                .toolCalls(List.of(new AssistantMessage.ToolCall("call-" + ++ids, "function", tool, json)))
                .build());
        return this;
    }

    ScriptedChatModel thenAnswer(String text) {
        replies.add(AssistantMessage.builder().content(text).build());
        return this;
    }

    @Override
    public ChatResponse call(Prompt prompt) {
        prompts.add(prompt);
        AssistantMessage reply = replies.isEmpty() ? AssistantMessage.builder().content("Done.").build() : replies.poll();
        return new ChatResponse(List.of(new Generation(reply)));
    }

    @Override
    public ChatOptions getOptions() {
        return ToolCallingChatOptions.builder().build();
    }

    /** Everything the model received, as text: messages, tool calls, tool results and tool definitions. */
    String everythingSent() {
        return ModelTraffic.toText(prompts);
    }
}
