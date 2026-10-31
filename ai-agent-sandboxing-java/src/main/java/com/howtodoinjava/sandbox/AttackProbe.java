package com.howtodoinjava.sandbox;

import java.net.ServerSocket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;

/**
 * Runs one attack against one sandbox and prints the outcome. Used by run-attack-matrix.sh,
 * which starts a fresh JVM per case so that a crash in one case can't affect the others.
 */
public class AttackProbe {

    public static void main(String[] args) throws Exception {
        CodeSandbox sandbox = sandbox(args[0]);
        Attack attack = Attack.valueOf(args[1]);

        Path secretFile = Files.createTempFile("orders-db", ".properties");
        Files.writeString(secretFile, "db.password=s3cr3t-from-file");

        try (ServerSocket server = new ServerSocket(0)) {
            String code = switch (attack) {
                case READ_FILE -> attack.code(secretFile);
                case OPEN_SOCKET -> attack.code(server.getLocalPort());
                default -> attack.code();
            };
            long start = System.nanoTime();
            ExecutionResult result = sandbox.run(code);
            long millis = (System.nanoTime() - start) / 1_000_000;
            String output = result.output() == null ? "" : result.output().lines().findFirst().orElse("");
            System.out.printf("RESULT|%s|%s|%s|%d ms|%s%n",
                    sandbox.name(), attack, result.status(), millis, output);
        } finally {
            Files.deleteIfExists(secretFile);
        }
    }

    static CodeSandbox sandbox(String name) {
        return switch (name) {
            case "unsafe" -> new UnsafeExecutor();
            case "constrained" -> new ConstrainedSandbox(1_000_000, Duration.ofSeconds(2));
            case "constrained-30s" -> new ConstrainedSandbox(1_000_000, Duration.ofSeconds(30));
            case "untrusted" -> new UntrustedSandbox();
            default -> throw new IllegalArgumentException(name);
        };
    }
}
