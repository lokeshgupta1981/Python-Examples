package com.howtodoinjava.ai.eval;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;

import org.springframework.ai.evaluation.EvaluationRequest;
import org.springframework.ai.evaluation.EvaluationResponse;

import tools.jackson.databind.json.JsonMapper;

/**
 * Runs the chosen setups once on the whole test set, grades each answer in code and appends
 * one CSV line per call to results/raw-results.csv.
 * Usage: EvalRunner RUN_NUMBER [setup name prefixes...]
 */
public class EvalRunner {

    static final String OLLAMA_URL = System.getenv().getOrDefault("OLLAMA_URL", "http://localhost:11434");
    static final Path RESULTS = Path.of("results", "raw-results.csv");

    static final List<Setup> SETUPS = List.of(
            new Setup("qwen2.5:3b zero-shot", "qwen2.5:3b", Prompts.ZERO_SHOT, 0.0, 40),
            new Setup("qwen2.5:3b few-shot", "qwen2.5:3b", Prompts.FEW_SHOT, 0.0, 40),
            new Setup("qwen3:1.7b zero-shot", "qwen3:1.7b", Prompts.ZERO_SHOT, 0.0, 40),
            new Setup("qwen3:1.7b few-shot", "qwen3:1.7b", Prompts.FEW_SHOT, 0.0, 40));

    public static void main(String[] args) throws IOException {
        int run = args.length > 0 ? Integer.parseInt(args[0]) : 1;
        List<String> only = args.length > 1 ? List.of(args).subList(1, args.length) : List.of();
        List<Ticket> tickets = loadTickets();

        for (Setup setup : SETUPS) {
            if (!only.isEmpty() && only.stream().noneMatch(setup.name()::startsWith)) {
                continue;
            }
            TicketClassifier classifier = new TicketClassifier(OLLAMA_URL, setup);
            classifier.classify("Warm-up call, not graded.");   // loads the model, so load time isn't measured

            long start = System.nanoTime();
            for (Ticket ticket : tickets) {
                ModelAnswer answer = classifier.classify(ticket.text());
                EvaluationResponse grade = new ExactMatchEvaluator(ticket)
                        .evaluate(new EvaluationRequest(ticket.text(), answer.content()));
                save(new Result(setup.name(), run, ticket.id(), grade.isPass(),
                        (boolean) grade.getMetadata().getOrDefault("categoryOk", false),
                        (boolean) grade.getMetadata().getOrDefault("priorityOk", false),
                        answer.promptTokens(), answer.outputTokens(),
                        answer.latencyMillis(), answer.computeMillis(),
                        answer.content().replaceAll("\\s+", " ")));
            }
            System.out.printf("%-22s run %d: %d tickets in %.1f s%n", setup.name(), run,
                    tickets.size(), (System.nanoTime() - start) / 1e9);
        }
    }

    static List<Ticket> loadTickets() throws IOException {
        JsonMapper json = JsonMapper.builder().build();
        try (InputStream in = EvalRunner.class.getResourceAsStream("/tickets.jsonl")) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8).lines()
                    .filter(line -> !line.isBlank())
                    .map(line -> json.readValue(line, Ticket.class))
                    .toList();
        }
    }

    private static void save(Result result) throws IOException {
        Files.createDirectories(RESULTS.getParent());
        if (Files.notExists(RESULTS)) {
            Files.writeString(RESULTS, Result.CSV_HEADER + System.lineSeparator());
        }
        Files.writeString(RESULTS, result.toCsv() + System.lineSeparator(), StandardOpenOption.APPEND);
    }
}
