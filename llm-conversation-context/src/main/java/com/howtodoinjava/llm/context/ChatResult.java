package com.howtodoinjava.llm.context;

/**
 * The reply and the token counts that Ollama reports for one /api/chat call.
 */
public record ChatResult(String content, int promptTokens, int cachedTokens,
                         int outputTokens, long millis) {
}
