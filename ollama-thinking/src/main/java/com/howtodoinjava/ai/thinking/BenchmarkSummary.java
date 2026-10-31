package com.howtodoinjava.ai.thinking;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

/** Reads results/*.csv written by ThinkingBenchmark and prints one line per setting. */
public class BenchmarkSummary {

    public static void main(String[] args) throws Exception {
        List<Path> files;
        try (Stream<Path> s = Files.list(Path.of("results"))) {
            files = s.filter(p -> p.toString().endsWith(".csv")).sorted().toList();
        }
        System.out.printf("%-28s %8s %9s %8s %10s %9s %9s %10s%n", "file", "correct", "thinking", "answer",
            "truncated", "p50 s", "mean s", "total s");
        for (Path file : files) {
            List<String[]> rows = Files.readAllLines(file).stream().skip(1).map(l -> l.split(",")).toList();
            int n = rows.size();
            long correct = rows.stream().filter(r -> r[2].equals("true")).count();
            double thinking = rows.stream().mapToInt(r -> Integer.parseInt(r[3])).average().orElse(0);
            double answer = rows.stream().mapToInt(r -> Integer.parseInt(r[4])).average().orElse(0);
            long truncated = rows.stream().filter(r -> r[6].equals("length")).count();
            long[] millis = rows.stream().mapToLong(r -> Long.parseLong(r[7])).sorted().toArray();
            double p50 = n % 2 == 1 ? millis[n / 2] : (millis[n / 2 - 1] + millis[n / 2]) / 2.0;
            long total = java.util.Arrays.stream(millis).sum();
            System.out.printf("%-28s %4d/%-3d %9.0f %8.1f %6d/%-3d %9.1f %9.1f %10.1f%n",
                file.getFileName(), correct, n, thinking, answer, truncated, n,
                p50 / 1000.0, total / 1000.0 / n, total / 1000.0);
        }
    }

    private BenchmarkSummary() {
    }
}
