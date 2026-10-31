package com.howtodoinjava.leastprivilege.agent;

import java.util.ArrayList;
import java.util.List;

import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.ChatOptions;
import org.springframework.ai.chat.prompt.Prompt;

/** Passes every call to the real model and keeps a copy of what was sent. */
public class RecordingChatModel implements ChatModel {

    private final ChatModel delegate;
    private final List<Prompt> prompts = new ArrayList<>();

    public RecordingChatModel(ChatModel delegate) {
        this.delegate = delegate;
    }

    @Override
    public ChatResponse call(Prompt prompt) {
        prompts.add(prompt);
        return delegate.call(prompt);
    }

    @Override
    public ChatOptions getOptions() {
        return delegate.getOptions();
    }

    public String everythingSent() {
        return ModelTraffic.toText(prompts);
    }
}
