package com.howtodoinjava.llm.context;

import java.util.ArrayList;
import java.util.List;

public class SlidingWindow implements ContextStrategy {

    private final int maxTurns;

    public SlidingWindow(int maxTurns) {
        this.maxTurns = maxTurns;
    }

    @Override
    public String name() {
        return "Sliding window (" + maxTurns + " turns)";
    }

    @Override
    public List<Message> messagesFor(String systemPrompt, List<Turn> turns, String userMessage) {
        List<Message> messages = new ArrayList<>();
        messages.add(Message.system(systemPrompt));
        for (Turn turn : turns.subList(Math.max(0, turns.size() - maxTurns), turns.size())) {
            messages.add(Message.user(turn.user()));
            messages.add(Message.assistant(turn.assistant()));
        }
        messages.add(Message.user(userMessage));
        return messages;
    }
}
