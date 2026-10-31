package com.howtodoinjava.llm.context;

/**
 * One finished exchange: what the user asked, what the model answered, and what it cost.
 */
public record Turn(String user, String assistant, ChatResult result) {
}
