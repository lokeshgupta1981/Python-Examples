package com.howtodoinjava.sandbox;

/**
 * Runs a short piece of JavaScript written by the model and returns what it produced.
 */
public interface CodeSandbox {

    String name();

    ExecutionResult run(String code);
}
