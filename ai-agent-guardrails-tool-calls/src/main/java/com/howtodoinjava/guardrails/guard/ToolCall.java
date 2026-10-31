package com.howtodoinjava.guardrails.guard;

import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

/**
 * One tool call the model asked for, together with who it runs for.
 * The user, role and customer come from our application, never from the model.
 */
public record ToolCall(String user, String role, String customerId, String tool, Map<String, Object> args) {

    public String text(String name) {
        Object value = args.get(name);
        return value == null ? null : value.toString();
    }

    /** Reads a number argument; throws IllegalArgumentException if it isn't one. */
    public BigDecimal decimal(String name) {
        Object value = args.get(name);
        if (value == null) {
            throw new IllegalArgumentException("missing argument '" + name + "'");
        }
        try {
            return new BigDecimal(value.toString().trim());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("argument '" + name + "' is not a number: " + value);
        }
    }

    /**
     * SHA-256 over user, tool and arguments in a fixed order. Numbers are normalized,
     * so 450, 450.0 and "450.00" give the same hash.
     */
    public String fingerprint() {
        String canonicalArgs = new TreeMap<>(args).entrySet().stream()
                .map(e -> e.getKey() + "=" + canonical(e.getValue()))
                .collect(Collectors.joining("&"));
        String input = user + "|" + tool + "|" + canonicalArgs;
        try {
            byte[] hash = MessageDigest.getInstance("SHA-256").digest(input.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    private static String canonical(Object value) {
        if (value == null) {
            return "";
        }
        String text = value.toString().trim();
        try {
            return new BigDecimal(text).stripTrailingZeros().toPlainString();
        } catch (NumberFormatException notANumber) {
            return text;
        }
    }
}
