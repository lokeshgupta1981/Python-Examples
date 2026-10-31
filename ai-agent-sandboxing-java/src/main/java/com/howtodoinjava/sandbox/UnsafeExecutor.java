package com.howtodoinjava.sandbox;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

import java.io.ByteArrayOutputStream;

/**
 * DO NOT USE: runs the code with full access to the host JVM. Here only for contrast.
 */
public class UnsafeExecutor implements CodeSandbox {

    @Override
    public String name() {
        return "Unsafe (allowAllAccess)";
    }

    @Override
    public ExecutionResult run(String code) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try (Context context = Context.newBuilder("js")
                .allowAllAccess(true)
                .out(out)
                .err(new ByteArrayOutputStream())
                .option("engine.WarnInterpreterOnly", "false")
                .build()) {
            Value result = context.eval("js", code);
            return ExecutionResult.ok(out + String.valueOf(result));
        } catch (PolyglotException e) {
            return ExecutionResult.from(e, false);
        }
    }
}
