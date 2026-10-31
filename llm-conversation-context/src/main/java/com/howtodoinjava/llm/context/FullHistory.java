package com.howtodoinjava.llm.context;

import java.util.ArrayList;
import java.util.List;

public class FullHistory implements ContextStrategy {

    @Override
    public String name() {
        return "Full history";
    }

    @Override
    public List<Message> messagesFor(String systemPrompt, List<Turn> turns, String userMessage) {
        List<Message> messages = new ArrayList<>();
        messages.add(Message.system(systemPrompt));
        for (Turn turn : turns) {
            messages.add(Message.user(turn.user()));
            messages.add(Message.assistant(turn.assistant()));
        }
        messages.add(Message.user(userMessage));
        return messages;
    }
}
