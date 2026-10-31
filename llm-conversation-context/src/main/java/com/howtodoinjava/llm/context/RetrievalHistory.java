package com.howtodoinjava.llm.context;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.IntStream;

/**
 * Sends the newest turns as they are, plus the older turns that are most
 * similar to the new question, found with embeddings.
 */
public class RetrievalHistory implements ContextStrategy {

    private final OllamaClient client;
    private final String embeddingModel;
    private final int windowTurns;
    private final int topK;
    private final List<float[]> turnVectors = new ArrayList<>();
    private int extraCalls = 0;
    private List<Integer> lastRetrieved = List.of();

    public RetrievalHistory(OllamaClient client, String embeddingModel, int windowTurns, int topK) {
        this.client = client;
        this.embeddingModel = embeddingModel;
        this.windowTurns = windowTurns;
        this.topK = topK;
    }

    @Override
    public String name() {
        return "Retrieval (" + windowTurns + " + top " + topK + ")";
    }

    @Override
    public List<Message> messagesFor(String systemPrompt, List<Turn> turns, String userMessage) {
        while (turnVectors.size() < turns.size()) {
            Turn turn = turns.get(turnVectors.size());
            turnVectors.add(embed("search_document: User: " + turn.user()
                + "\nAssistant: " + turn.assistant()));
        }

        int windowStart = Math.max(0, turns.size() - windowTurns);
        List<Message> messages = new ArrayList<>();
        messages.add(Message.system(systemPrompt));

        if (windowStart > 0) {
            float[] question = embed("search_query: " + userMessage);
            lastRetrieved = IntStream.range(0, windowStart).boxed()
                .sorted(Comparator.comparingDouble((Integer i) -> -cosine(question, turnVectors.get(i))))
                .limit(topK)
                .sorted()
                .toList();
            for (int i : lastRetrieved) {
                messages.add(Message.user(turns.get(i).user()));
                messages.add(Message.assistant(turns.get(i).assistant()));
            }
        }
        for (Turn turn : turns.subList(windowStart, turns.size())) {
            messages.add(Message.user(turn.user()));
            messages.add(Message.assistant(turn.assistant()));
        }
        messages.add(Message.user(userMessage));
        return messages;
    }

    private float[] embed(String text) {
        extraCalls++;
        return client.embed(embeddingModel, text);
    }

    static double cosine(float[] a, float[] b) {
        double dot = 0, normA = 0, normB = 0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    /** Turn numbers (1-based) added to the last request. */
    public List<Integer> lastRetrieved() {
        return lastRetrieved.stream().map(i -> i + 1).toList();
    }

    @Override
    public int extraCalls() {
        return extraCalls;
    }
}
