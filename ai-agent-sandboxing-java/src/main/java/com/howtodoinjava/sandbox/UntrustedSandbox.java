package com.howtodoinjava.sandbox;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.HostAccess;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.SandboxPolicy;
import org.graalvm.polyglot.Value;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;

/**
 * Runs the code in a separate GraalVM isolate (its own heap) with SandboxPolicy.UNTRUSTED.
 * Needs the js-isolate-community (or js-isolate) dependency.
 */
public class UntrustedSandbox implements CodeSandbox {

    @Override
    public String name() {
        return "GraalVM UNTRUSTED";
    }

    @Override
    public ExecutionResult run(String code) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ByteArrayOutputStream err = new ByteArrayOutputStream();
        try (Context context = Context.newBuilder("js")
                .sandbox(SandboxPolicy.UNTRUSTED)
                .in(new ByteArrayInputStream(new byte[0]))
                .out(out)
                .err(err)
                .allowHostAccess(HostAccess.UNTRUSTED)
                .option("engine.MaxIsolateMemory", "256MB")
                .option("sandbox.MaxHeapMemory", "64MB")
                .option("sandbox.MaxCPUTime", "2s")
                .option("sandbox.MaxThreads", "1")
                .option("sandbox.MaxASTDepth", "100")
                .option("sandbox.MaxOutputStreamSize", "16KB")
                .option("sandbox.MaxErrorStreamSize", "16KB")
                .build()) {
            Value result = context.eval("js", code);
            return ExecutionResult.ok(out + String.valueOf(result));
        } catch (PolyglotException e) {
            return ExecutionResult.from(e, false);
        }
    }
}
