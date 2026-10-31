package com.howtodoinjava.guardrails.guard;

/**
 * One check between the model's tool call and the tool.
 */
public interface Gate {

    /** Returns ALLOW to pass the call on to the next gate. */
    Decision check(ToolCall call);

    /** Called on every gate once all gates allowed the call, right before the tool runs. */
    default void onAllowed(ToolCall call) {
    }
}
