package com.howtodoinjava.sandbox;

import org.graalvm.polyglot.PolyglotException;

/**
 * The outcome of one run: the value or output on success, otherwise the reason it stopped.
 */
public record ExecutionResult(Status status, String output) {

    public enum Status { OK, ERROR, LIMIT_EXCEEDED, TIMED_OUT }

    public static ExecutionResult ok(String output) {
        return new ExecutionResult(Status.OK, output);
    }

    public static ExecutionResult from(PolyglotException e, boolean timedOut) {
        if (timedOut) {
            return new ExecutionResult(Status.TIMED_OUT, e.getMessage());
        }
        if (e.isResourceExhausted()) {
            return new ExecutionResult(Status.LIMIT_EXCEEDED, e.getMessage());
        }
        return new ExecutionResult(Status.ERROR, e.getMessage());
    }

    public boolean succeeded() {
        return status == Status.OK;
    }
}
