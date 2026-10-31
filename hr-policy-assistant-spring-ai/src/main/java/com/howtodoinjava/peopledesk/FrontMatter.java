package com.howtodoinjava.peopledesk;

import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.Map;

/** Splits "key: value" front matter between two "---" lines from the Markdown body. */
public record FrontMatter(Map<String, Object> metadata, String body) {

    public static FrontMatter parse(String markdown) {
        String[] parts = markdown.split("(?m)^---\\s*$", 3);
        if (parts.length < 3 || !parts[0].isBlank()) {
            throw new IllegalArgumentException("Policy file must start with front matter");
        }
        Map<String, Object> metadata = new LinkedHashMap<>();
        for (String line : parts[1].strip().split("\\R")) {
            String[] kv = line.split(":", 2);
            String key = kv[0].strip();
            String value = kv[1].strip();
            metadata.put(key, key.startsWith("effective_") ? toNumber(value) : value);
        }
        return new FrontMatter(metadata, parts[2]);
    }

    // 2026-04-01 -> 20260401, so the vector store can compare dates as numbers
    static int toNumber(String isoDate) {
        LocalDate date = LocalDate.parse(isoDate);
        return date.getYear() * 10_000 + date.getMonthValue() * 100 + date.getDayOfMonth();
    }
}
