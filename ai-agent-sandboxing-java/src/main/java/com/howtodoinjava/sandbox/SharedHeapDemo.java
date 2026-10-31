package com.howtodoinjava.sandbox;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Shows that a CONSTRAINED context shares the host heap: while the guest runs a memory bomb,
 * a host thread that serves "other requests" (allocating 1 MB every 10 ms) records the heap usage
 * and counts its own OutOfMemoryErrors.
 * Run with -Xmx512m. Pass "untrusted" to run the same bomb in the UNTRUSTED isolate instead.
 */
public class SharedHeapDemo {

    public static void main(String[] args) throws Exception {
        AtomicInteger served = new AtomicInteger();
        AtomicInteger failed = new AtomicInteger();
        AtomicLong peakUsedMb = new AtomicLong();
        Runtime jvm = Runtime.getRuntime();

        Thread otherRequests = Thread.ofPlatform().daemon().start(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    byte[] response = new byte[1024 * 1024];
                    response[0] = 1;
                    served.incrementAndGet();
                    peakUsedMb.accumulateAndGet((jvm.totalMemory() - jvm.freeMemory()) >> 20, Math::max);
                } catch (OutOfMemoryError e) {
                    failed.incrementAndGet();
                }
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    return;
                }
            }
        });

        CodeSandbox sandbox = args.length > 0 && args[0].equals("untrusted")
                ? new UntrustedSandbox()
                : new ConstrainedSandbox(1_000_000, Duration.ofSeconds(30));
        ExecutionResult result = sandbox.run(Attack.MEMORY_BOMB.code());
        otherRequests.interrupt();

        System.out.println(sandbox.name() + " result: " + result.status() + " - " + result.output());
        System.out.println("Host heap: max " + (jvm.maxMemory() >> 20) + " MB, peak used " + peakUsedMb.get() + " MB");
        System.out.println("Host requests served: " + served.get() + ", failed with OutOfMemoryError: " + failed.get());
    }
}
