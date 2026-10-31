package com.howtodoinjava.ai.eval;

/** One configuration we want to compare: which model, which prompt, which settings. */
public record Setup(String name, String model, String systemPrompt, double temperature, int maxTokens) {
}
