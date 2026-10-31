package com.howtodoinjava.llm.context;

import java.util.ArrayList;
import java.util.List;

/**
 * Keeps as many recent turns as fit into a token budget. The size of each turn
 * comes from the token counts Ollama reports, not from counting characters.
 */
public class TokenBudget implements ContextStrategy {

    private final int budget;
    private final List<Integer> turnTokens = new ArrayList<>();
    private int firstKept = 0;
    private int historyTokensSent = 0;

    public TokenBudget(int budget) {
        this.budget = budget;
    }

    @Override
    public String name() {
        return "Token budget (" + budget + ")";
    }

    @Override
    public List<Message> messagesFor(String systemPrompt, List<Turn> turns, String userMessage) {
        if (turns.size() > turnTokens.size()) {
            // prompt + reply of the last call, minus the history we sent with it,
            // is what the newest turn adds to the next prompt
            ChatResult last = turns.getLast().result();
            turnTokens.add(last.promptTokens() + last.outputTokens() - historyTokensSent);
        }

        int total = turnTokens.subList(firstKept, turnTokens.size())
            .stream().mapToInt(Integer::intValue).sum();
        while (total > budget && firstKept < turns.size()) {
            total -= turnTokens.get(firstKept++);
        }
        historyTokensSent = total;

        List<Message> messages = new ArrayList<>();
        messages.add(Message.system(systemPrompt));
        for (Turn turn : turns.subList(firstKept, turns.size())) {
            messages.add(Message.user(turn.user()));
            messages.add(Message.assistant(turn.assistant()));
        }
        messages.add(Message.user(userMessage));
        return messages;
    }
}
