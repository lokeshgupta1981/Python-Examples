package com.howtodoinjava.ai.eval;

/** One labelled test case: the ticket text and the answer a person decided is correct. */
public record Ticket(String id, String text, String category, String priority) {
}
