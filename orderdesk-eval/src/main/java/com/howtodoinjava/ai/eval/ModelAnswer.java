package com.howtodoinjava.ai.eval;

/**
 * The raw answer plus what it cost: tokens in, tokens out, the time we waited (latency)
 * and the time the model spent computing (Ollama's prompt-eval plus eval duration).
 */
public record ModelAnswer(String content, int promptTokens, int outputTokens,
        long latencyMillis, long computeMillis) {
}
