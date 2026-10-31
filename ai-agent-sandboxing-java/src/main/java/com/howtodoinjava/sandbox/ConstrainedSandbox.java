package com.howtodoinjava.sandbox;

import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.ResourceLimits;
import org.graalvm.polyglot.SandboxPolicy;
import org.graalvm.polyglot.Value;

import java.io.ByteArrayOutputStream;
import java.time.Duration;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Runs the code in the same JVM with SandboxPolicy.CONSTRAINED, a statement limit and a timeout.
 */
public class ConstrainedSandbox implements CodeSandbox {

    private static final ScheduledExecutorService WATCHDOG =
            Executors.newSingleThreadScheduledExecutor(r -> {
                Thread t = new Thread(r, "sandbox-watchdog");
                t.setDaemon(true);
                return t;
            });

    private final long maxStatements;
    private final Duration timeout;

    public ConstrainedSandbox(long maxStatements, Duration timeout) {
        this.maxStatements = maxStatements;
        this.timeout = timeout;
    }

    @Override
    public String name() {
        return "GraalVM CONSTRAINED";
    }

    @Override
    public ExecutionResult run(String code) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ResourceLimits limits = ResourceLimits.newBuilder()
                .statementLimit(maxStatements, null)
                .build();
        AtomicBoolean timedOut = new AtomicBoolean();

        try (Context context = Context.newBuilder("js")
                .sandbox(SandboxPolicy.CONSTRAINED)
                .out(out)
                .err(new ByteArrayOutputStream())
                .option("engine.WarnInterpreterOnly", "false")
                .resourceLimits(limits)
                .build()) {
            var watchdog = WATCHDOG.schedule(() -> {
                timedOut.set(true);
                context.close(true);
            }, timeout.toMillis(), TimeUnit.MILLISECONDS);
            try {
                Value result = context.eval("js", code);
                return ExecutionResult.ok(out + String.valueOf(result));
            } finally {
                watchdog.cancel(false);
            }
        } catch (PolyglotException e) {
            return ExecutionResult.from(e, timedOut.get());
        }
    }
}
