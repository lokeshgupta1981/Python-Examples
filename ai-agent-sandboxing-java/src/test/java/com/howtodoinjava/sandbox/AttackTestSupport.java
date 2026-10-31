package com.howtodoinjava.sandbox;

import java.io.IOException;
import java.net.ServerSocket;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Prepares the targets of the attacks: a secret file and a listening local port.
 */
class AttackTestSupport implements AutoCloseable {

    static final String ENV_SECRET = "s3cr3t-from-env";     // set by Surefire, see pom.xml
    static final String FILE_SECRET = "s3cr3t-from-file";

    final Path secretFile;
    final ServerSocket server;

    AttackTestSupport() throws IOException {
        secretFile = Files.createTempFile("orders-db", ".properties");
        Files.writeString(secretFile, "db.password=" + FILE_SECRET);
        server = new ServerSocket(0);
    }

    String codeFor(Attack attack) {
        return switch (attack) {
            case READ_FILE -> attack.code(secretFile);
            case OPEN_SOCKET -> attack.code(server.getLocalPort());
            default -> attack.code();
        };
    }

    @Override
    public void close() throws IOException {
        server.close();
        Files.deleteIfExists(secretFile);
    }
}
