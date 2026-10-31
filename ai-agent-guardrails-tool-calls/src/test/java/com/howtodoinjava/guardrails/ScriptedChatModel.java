package com.howtodoinjava.guardrails;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.Generation;
import org.springframework.ai.chat.prompt.ChatOptions;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.model.tool.ToolCallingChatOptions;

/**
 * Plays a model that an attacker has already talked into something: it returns
 * the tool calls we script, in order, and records every prompt it receives.
 */
public class ScriptedChatModel implements ChatModel {

    private final Deque<AssistantMessage> replies = new ArrayDeque<>();
    private final List<Prompt> prompts = new ArrayList<>();
    private final AtomicInteger ids = new AtomicInteger();

    /** The model asks for these tool calls, given as "name", "json" pairs. */
    public ScriptedChatModel thenCall(String... nameAndJsonPairs) {
        List<AssistantMessage.ToolCall> calls = new ArrayList<>();
        for (int i = 0; i < nameAndJsonPairs.length; i += 2) {
            calls.add(new AssistantMessage.ToolCall("call-" + ids.incrementAndGet(), "function",
                    nameAndJsonPairs[i], nameAndJsonPairs[i + 1]));
        }
        replies.add(AssistantMessage.builder().content("").toolCalls(calls).build());
        return this;
    }

    public ScriptedChatModel thenAnswer(String text) {
        replies.add(AssistantMessage.builder().content(text).build());
        return this;
    }

    @Override
    public ChatResponse call(Prompt prompt) {
        prompts.add(prompt);
        AssistantMessage reply = replies.isEmpty()
                ? AssistantMessage.builder().content("Done.").build()
                : replies.poll();
        return new ChatResponse(List.of(new Generation(reply)));
    }

    @Override
    public ChatOptions getOptions() {
        return ToolCallingChatOptions.builder().build();
    }

    public List<Prompt> prompts() {
        return prompts;
    }

    /** Names of the tools the model was offered in the first request. */
    public List<String> offeredTools() {
        ToolCallingChatOptions options = (ToolCallingChatOptions) prompts.getFirst().getOptions();
        return options.getToolCallbacks().stream().map(t -> t.getToolDefinition().name()).sorted().toList();
    }
}
