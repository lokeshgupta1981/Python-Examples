package com.howtodoinjava.ai.eval;

import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

/** Reads results/raw-results.csv and prints the tables we compare setups with. */
public final class Report {

    private Report() {
    }

    public static void main(String[] args) throws IOException {
        List<Result> results = Files.readAllLines(EvalRunner.RESULTS).stream()
                .skip(1)
                .map(Result::fromCsv)
                .toList();
        print(results, EvalRunner.loadTickets().size());
    }

    static void print(List<Result> results, int n) {
        Map<String, List<Result>> bySetup = results.stream()
                .collect(Collectors.groupingBy(Result::setup, LinkedHashMap::new, Collectors.toList()));

        System.out.println("Accuracy per run (both labels right), with 95% margin of error:");
        for (var entry : bySetup.entrySet()) {
            Map<Integer, List<Result>> byRun = entry.getValue().stream()
                    .collect(Collectors.groupingBy(Result::run, LinkedHashMap::new, Collectors.toList()));
            StringBuilder line = new StringBuilder("%-22s".formatted(entry.getKey()));
            for (var run : byRun.entrySet()) {
                long correct = run.getValue().stream().filter(Result::pass).count();
                double p = (double) correct / n;
                line.append("  run %d: %d/%d = %.1f%% +/- %.1f".formatted(
                        run.getKey(), correct, n, 100 * p, 100 * Stats.marginOfError(p, n)));
            }
            System.out.println(line);
        }

        System.out.println();
        System.out.println("Per field, all runs:");
        for (var entry : bySetup.entrySet()) {
            List<Result> rs = entry.getValue();
            long catOk = rs.stream().filter(Result::categoryOk).count();
            long prioOk = rs.stream().filter(Result::priorityOk).count();
            System.out.printf("%-22s category %.1f%%  priority %.1f%%%n", entry.getKey(),
                    100.0 * catOk / rs.size(), 100.0 * prioOk / rs.size());
        }

        System.out.println();
        System.out.println("Cost per setup, latest run of each setup:");
        System.out.printf("%-22s %8s %7s %7s %8s %8s %10s %11s %12s%n", "setup", "accuracy", "in tok",
                "out tok", "p50 ms", "p95 ms", "compute ms", "tok/correct", "s/correct");
        for (var entry : bySetup.entrySet()) {
            int latestRun = entry.getValue().stream().mapToInt(Result::run).max().orElse(1);
            List<Result> rs = entry.getValue().stream()
                    .filter(r -> r.run() == latestRun)
                    .toList();
            long correct = rs.stream().filter(Result::pass).count();
            double inTokens = rs.stream().mapToInt(Result::promptTokens).average().orElse(0);
            double outTokens = rs.stream().mapToInt(Result::outputTokens).average().orElse(0);
            List<Long> latencies = rs.stream().map(Result::latencyMillis).toList();
            List<Long> compute = rs.stream().map(Result::computeMillis).toList();
            long totalTokens = rs.stream().mapToLong(r -> r.promptTokens() + r.outputTokens()).sum();
            double computeSeconds = rs.stream().mapToLong(Result::computeMillis).sum() / 1000.0;
            System.out.printf("%-22s %7.1f%% %7.0f %7.1f %8d %8d %10d %11.0f %12.2f%n", entry.getKey(),
                    100.0 * correct / rs.size(), inTokens, outTokens,
                    Stats.percentile(latencies, 0.5), Stats.percentile(latencies, 0.95),
                    Stats.percentile(compute, 0.5), (double) totalTokens / correct,
                    computeSeconds / correct);
        }

        System.out.println();
        System.out.println("Answers that changed between run 1 and run 2:");
        for (var entry : bySetup.entrySet()) {
            Map<String, String> first = new LinkedHashMap<>();
            int changed = 0;
            int compared = 0;
            for (Result r : entry.getValue()) {
                String labels = r.categoryOk() + "/" + r.priorityOk() + "/" + r.answer().replace(" ", "");
                if (r.run() == 1) {
                    first.put(r.ticketId(), labels);
                } else if (r.run() == 2) {
                    compared++;
                    if (!Objects.equals(first.get(r.ticketId()), labels)) {
                        changed++;
                    }
                }
            }
            if (compared > 0) {
                System.out.printf("%-22s %d of %d%n", entry.getKey(), changed, compared);
            }
        }

        System.out.println();
        System.out.println("Paired comparison on run 1 (tickets only one of the two got right):");
        List<String> names = new ArrayList<>(bySetup.keySet());
        for (int i = 0; i < names.size(); i++) {
            for (int j = i + 1; j < names.size(); j++) {
                Map<String, Boolean> a = passes(bySetup.get(names.get(i)));
                Map<String, Boolean> b = passes(bySetup.get(names.get(j)));
                long onlyA = a.keySet().stream().filter(id -> a.get(id) && !b.getOrDefault(id, false)).count();
                long onlyB = a.keySet().stream().filter(id -> !a.get(id) && b.getOrDefault(id, false)).count();
                System.out.printf("%-22s vs %-22s only first: %d, only second: %d%n",
                        names.get(i), names.get(j), onlyA, onlyB);
            }
        }

        System.out.println();
        System.out.println("Wrong answers in run 1:");
        for (Result r : results) {
            if (r.run() == 1 && !r.pass()) {
                System.out.printf("%-22s %s %s%n", r.setup(), r.ticketId(), r.answer());
            }
        }
    }

    private static Map<String, Boolean> passes(List<Result> results) {
        Map<String, Boolean> map = new LinkedHashMap<>();
        results.stream().filter(r -> r.run() == 1).forEach(r -> map.put(r.ticketId(), r.pass()));
        return map;
    }
}
