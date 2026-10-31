package com.howtodoinjava.llm.context;

import java.util.List;

/**
 * Decides which messages go into the next request.
 */
public interface ContextStrategy {

    String name();

    List<Message> messagesFor(String systemPrompt, List<Turn> turns, String userMessage);

    /** Model calls made only to manage the context (summaries, embeddings). */
    default int extraCalls() {
        return 0;
    }
}
