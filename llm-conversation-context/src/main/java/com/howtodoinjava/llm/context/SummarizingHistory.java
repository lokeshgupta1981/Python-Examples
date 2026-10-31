package com.howtodoinjava.llm.context;

import java.util.ArrayList;
import java.util.List;

/**
 * When the last prompt went over the budget, replaces the older turns with a
 * short summary written by the same model. The newest turns stay word for word.
 */
public class SummarizingHistory implements ContextStrategy {

    private final OllamaClient client;
    private final int budget;
    private final int keepTurns;
    private String summary = "";
    private int summarizedTurns = 0;
    private int extraCalls = 0;

    public SummarizingHistory(OllamaClient client, int budget, int keepTurns) {
        this.client = client;
        this.budget = budget;
        this.keepTurns = keepTurns;
    }

    @Override
    public String name() {
        return "Summary (" + budget + ")";
    }

    @Override
    public List<Message> messagesFor(String systemPrompt, List<Turn> turns, String userMessage) {
        if (!turns.isEmpty()) {
            ChatResult last = turns.getLast().result();
            int nextPrompt = last.promptTokens() + last.outputTokens();
            int end = turns.size() - keepTurns;
            if (nextPrompt > budget && end > summarizedTurns) {
                summary = summarize(turns.subList(summarizedTurns, end));
                summarizedTurns = end;
            }
        }

        List<Message> messages = new ArrayList<>();
        messages.add(Message.system(summary.isEmpty() ? systemPrompt
            : systemPrompt + "\n\nSummary of the earlier conversation: " + summary));
        for (Turn turn : turns.subList(summarizedTurns, turns.size())) {
            messages.add(Message.user(turn.user()));
            messages.add(Message.assistant(turn.assistant()));
        }
        messages.add(Message.user(userMessage));
        return messages;
    }

    private String summarize(List<Turn> older) {
        StringBuilder text = new StringBuilder();
        if (!summary.isEmpty()) {
            text.append("Earlier summary: ").append(summary).append("\n\n");
        }
        for (Turn turn : older) {
            text.append("User: ").append(turn.user()).append('\n');
            text.append("Assistant: ").append(turn.assistant()).append('\n');
        }
        List<Message> request = List.of(
            Message.system("Summarize the conversation in at most 40 words. "
                + "Always keep the user's name, what they own and any decisions."),
            Message.user(text.toString()));
        extraCalls++;
        return client.chat(request, 80).content();
    }

    public String summary() {
        return summary;
    }

    @Override
    public int extraCalls() {
        return extraCalls;
    }
}
