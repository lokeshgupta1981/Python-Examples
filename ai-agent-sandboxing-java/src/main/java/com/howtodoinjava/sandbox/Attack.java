package com.howtodoinjava.sandbox;

/**
 * Malicious snippets that a prompt-injected agent could write. %s placeholders are filled by the caller.
 */
public enum Attack {

    READ_SECRET_ENV("Read DB_PASSWORD from the environment",
            "Java.type('java.lang.System').getenv('DB_PASSWORD')"),

    READ_FILE("Read a file from the host",
            "Java.type('java.nio.file.Files').readString(Java.type('java.nio.file.Path').of('%s'))"),

    OPEN_SOCKET("Open a network connection",
            "const s = new (Java.type('java.net.Socket'))('127.0.0.1', %s); s.close(); 'connected'"),

    RUN_PROCESS("Start an operating system process",
            "Java.type('java.lang.Runtime').getRuntime().exec(['id']).waitFor() === 0 ? 'process ran' : 'failed'"),

    INFINITE_LOOP("Burn CPU forever",
            "while (true) {}"),

    MEMORY_BOMB("Allocate memory until something breaks",
            "const keep = []; while (true) { keep.push(new Array(1000000).fill(42)); }");

    private final String description;
    private final String template;

    Attack(String description, String template) {
        this.description = description;
        this.template = template;
    }

    public String description() {
        return description;
    }

    public String code(Object... args) {
        return template.formatted(args);
    }
}
