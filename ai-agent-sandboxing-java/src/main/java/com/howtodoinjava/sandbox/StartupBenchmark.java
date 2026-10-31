package com.howtodoinjava.sandbox;

import java.util.Arrays;

/**
 * Measures how long one call of each sandbox takes for a tiny snippet:
 * the first call in a fresh JVM, and the median of the next 20 calls.
 * Run each sandbox in its own JVM: java ... StartupBenchmark constrained
 */
public class StartupBenchmark {

    public static void main(String[] args) {
        CodeSandbox sandbox = AttackProbe.sandbox(args[0]);
        String code = "[120.50, 75.00, 42.25].reduce((a, b) => a + b, 0)";

        long first = time(sandbox, code);
        long[] next = new long[20];
        for (int i = 0; i < next.length; i++) {
            next[i] = time(sandbox, code);
        }
        Arrays.sort(next);
        System.out.printf("BENCH|%s|first call %d ms|median of next 20: %d ms%n",
                sandbox.name(), first, next[next.length / 2]);
    }

    private static long time(CodeSandbox sandbox, String code) {
        long start = System.nanoTime();
        ExecutionResult result = sandbox.run(code);
        if (!result.succeeded()) {
            throw new IllegalStateException(result.output());
        }
        return (System.nanoTime() - start) / 1_000_000;
    }
}
