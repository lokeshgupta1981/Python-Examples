package com.howtodoinjava.ai.replies;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/**
 * Runs the labelled tickets through the drafter (mode "full"), or re-reads the stored
 * results to print the threshold table (mode "thresholds") or the results table (mode "summary").
 */
@Component
@Profile("eval")
public class EvalRunner implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(EvalRunner.class);
    private static final double[] THRESHOLDS = {0.50, 0.55, 0.60, 0.65, 0.70, 0.75};
    private static final int RETRIES = 3;
    private static final long RETRY_WAIT_MS = 30_000;

    @ConfigurationProperties("orderdesk.eval")
    public record EvalProperties(String mode, String tickets, String results, String review, int limit) {
    }

    public record Ticket(String id, String ticket, boolean covered, String expected, String keyFact) {
    }

    private final ReplyDrafter drafter;
    private final SimpleVectorStore helpIndex;
    private final ReplyProperties props;
    private final EvalProperties eval;
    private final JsonMapper json = JsonMapper.builder().build();

    public EvalRunner(ReplyDrafter drafter, SimpleVectorStore helpIndex,
                      ReplyProperties props, EvalProperties eval) {
        this.drafter = drafter;
        this.helpIndex = helpIndex;
        this.props = props;
        this.eval = eval;
    }

    @Override
    public void run(String... args) throws Exception {
        switch (eval.mode()) {
            case "full" -> runFull();
            case "thresholds" -> printThresholds(readResults());
            case "summary" -> printSummary(readResults());
            default -> throw new IllegalArgumentException("Unknown orderdesk.eval.mode: " + eval.mode());
        }
    }

    private void runFull() throws IOException, InterruptedException {
        List<Ticket> tickets = new ArrayList<>();
        for (String line : Files.readAllLines(Path.of(eval.tickets()))) {
            if (!line.isBlank()) {
                tickets.add(json.readValue(line, Ticket.class));
            }
        }
        if (eval.limit() > 0 && eval.limit() < tickets.size()) {
            tickets = tickets.subList(0, eval.limit());
        }
        Path out = Path.of(eval.results());
        Files.deleteIfExists(out);

        for (Ticket t : tickets) {
            // Score every article, ignoring the threshold, so Step 9 can try any threshold later.
            List<Document> all = helpIndex.similaritySearch(SearchRequest.builder()
                    .query(t.ticket()).topK(100).similarityThresholdAll().build());
            Map<String, Double> scores = new LinkedHashMap<>();
            all.forEach(d -> scores.put(ReplyDrafter.toSource(d).articleId(), round(d.getScore())));

            List<Document> top = all.subList(0, Math.min(props.topK(), all.size()));
            List<Document> passed = top.stream()
                    .filter(d -> d.getScore() >= props.similarityThreshold()).toList();
            boolean thresholdStopped = passed.isEmpty();
            // When the threshold stops a ticket, still ask the model, to test the covered flag alone.
            List<Document> sent = thresholdStopped ? top : passed;

            long start = System.currentTimeMillis();
            DraftReply reply = askWithRetry(t.ticket(), sent);
            long millis = System.currentTimeMillis() - start;
            DraftResult result = drafter.check("eval-" + t.id(), reply, sent);

            Set<String> cited = result.sources().stream()
                    .map(DraftResult.Source::articleId).collect(Collectors.toSet());
            String raw = reply == null || reply.replyText() == null ? "" : reply.replyText();
            boolean isDraft = result.status() == DraftResult.Status.DRAFT && !thresholdStopped;

            Map<String, Object> row = new LinkedHashMap<>();
            row.put("id", t.id());
            row.put("covered", t.covered());
            row.put("expected", t.expected());
            row.put("scores", scores);
            row.put("thresholdStopped", thresholdStopped);
            row.put("sentIds", sent.stream().map(d -> ReplyDrafter.toSource(d).articleId()).toList());
            row.put("modelCovered", reply != null && reply.covered());
            row.put("status", isDraft ? "DRAFT" : "NO_DRAFT");
            row.put("reason", result.reason());
            row.put("citedIds", cited);
            row.put("citesExpected", t.expected() != null && cited.contains(t.expected()));
            row.put("modelTypedLink", ReplyDrafter.LINK.matcher(raw).find());
            row.put("hasKeyFact", t.keyFact() != null
                    && raw.toLowerCase(Locale.ROOT).contains(t.keyFact().toLowerCase(Locale.ROOT)));
            row.put("modelReply", raw);
            row.put("millis", millis);
            Files.writeString(out, json.writeValueAsString(row) + "\n",
                    java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
            log.info("{} covered={} stopped={} status={} cited={} {} ms",
                    t.id(), t.covered(), thresholdStopped, row.get("status"), cited, millis);
        }
        printSummary(readResults());
    }

    private DraftReply askWithRetry(String ticket, List<Document> articles) throws InterruptedException {
        for (int attempt = 0; ; attempt++) {
            try {
                return drafter.askModel(ticket, articles);
            }
            catch (RuntimeException e) {
                if (attempt == RETRIES) {
                    throw e;
                }
                log.warn("Model call failed ({}), retrying in 30 s", e.getMessage());
                Thread.sleep(RETRY_WAIT_MS);
            }
        }
    }

    private List<JsonNode> readResults() throws IOException {
        List<JsonNode> rows = new ArrayList<>();
        for (String line : Files.readAllLines(Path.of(eval.results()))) {
            if (!line.isBlank()) {
                rows.add(json.readTree(line));
            }
        }
        return rows;
    }

    private void printThresholds(List<JsonNode> rows) {
        System.out.println("| Threshold | Covered tickets stopped | Expected article in top 3 above threshold "
                + "| Uncovered tickets passing |");
        System.out.println("|---|---|---|---|");
        for (double threshold : THRESHOLDS) {
            int stopped = 0, expectedAbove = 0, uncoveredPassing = 0;
            for (JsonNode row : rows) {
                List<Map.Entry<String, Double>> top = topK(row.get("scores"));
                boolean anyAbove = top.stream().anyMatch(e -> e.getValue() >= threshold);
                if (row.get("covered").asBoolean()) {
                    if (!anyAbove) {
                        stopped++;
                    }
                    String expected = row.get("expected").asString();
                    if (top.stream().anyMatch(e -> e.getKey().equals(expected) && e.getValue() >= threshold)) {
                        expectedAbove++;
                    }
                }
                else if (anyAbove) {
                    uncoveredPassing++;
                }
            }
            System.out.printf(Locale.ROOT, "| %.2f | %d | %d | %d |%n",
                    threshold, stopped, expectedAbove, uncoveredPassing);
        }
    }

    private List<Map.Entry<String, Double>> topK(JsonNode scores) {
        Map<String, Double> map = new LinkedHashMap<>();
        scores.properties().forEach(e -> map.put(e.getKey(), e.getValue().asDouble()));
        return map.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .limit(props.topK()).toList();
    }

    private void printSummary(List<JsonNode> rows) throws IOException {
        Set<String> unsupported = readReview();
        int covered = 0, drafts = 0, citesExpected = 0, links = 0, keyFact = 0, wrong = 0;
        int uncovered = 0, uncoveredNoDraft = 0;
        List<Long> times = new ArrayList<>();
        for (JsonNode row : rows) {
            boolean draft = "DRAFT".equals(row.get("status").asString());
            times.add(row.get("millis").asLong());
            if (row.get("modelTypedLink").asBoolean()) {
                links++;
            }
            if (row.get("covered").asBoolean()) {
                covered++;
                if (draft) {
                    drafts++;
                    if (row.get("citesExpected").asBoolean()) citesExpected++;
                    if (row.get("hasKeyFact").asBoolean()) keyFact++;
                    if (unsupported.contains(row.get("id").asString())) wrong++;
                }
            }
            else {
                uncovered++;
                if (!draft) uncoveredNoDraft++;
            }
        }
        times.sort(Comparator.naturalOrder());
        double median = times.isEmpty() ? 0 : times.size() % 2 == 1
                ? times.get(times.size() / 2)
                : (times.get(times.size() / 2 - 1) + times.get(times.size() / 2)) / 2.0;

        System.out.printf("Covered tickets with a draft: %d of %d%n", drafts, covered);
        System.out.printf("Drafts that cite the expected article: %d of %d%n", citesExpected, drafts);
        System.out.printf("Drafts with a link typed by the model: %d%n", links);
        System.out.printf("Drafts that contain the article's key fact: %d of %d%n", keyFact, drafts);
        System.out.printf("Drafts with a wrong or unsupported claim (review.csv): %s%n",
                unsupported.isEmpty() ? "not reviewed" : wrong + " of " + drafts);
        System.out.printf("Uncovered tickets with no draft: %d of %d%n", uncoveredNoDraft, uncovered);
        System.out.printf(Locale.ROOT, "Median model call: %.1f s%n", median / 1000.0);
    }

    /** review.csv: one line per ticket id with "yes" in the second column when the draft is wrong. */
    private Set<String> readReview() throws IOException {
        Path review = Path.of(eval.review());
        if (!Files.exists(review)) {
            return Set.of();
        }
        return Files.readAllLines(review).stream()
                .map(line -> line.split(","))
                .filter(parts -> parts.length >= 2 && parts[1].trim().equalsIgnoreCase("yes"))
                .map(parts -> parts[0].trim())
                .collect(Collectors.toSet());
    }

    private static double round(Double score) {
        return score == null ? 0.0 : Math.round(score * 1000.0) / 1000.0;
    }
}
