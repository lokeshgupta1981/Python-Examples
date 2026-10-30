package com.howtodoinjava.trailgear;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BiFunction;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

/**
 * Runs the labelled queries in data/queries.csv through every search and reports
 * hit@5 and MRR per query group. Active only with --spring.profiles.active=eval.
 */
@Component
@Profile("eval")
@Order(2)
public class Evaluator implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(Evaluator.class);
    private static final int TOP = 10;
    private static final List<String> METHODS = List.of("keyword", "semantic", "hybrid", "semantic_no_prefix");

    record QueryResult(String id, String group, String query, List<String> relevant,
                       Map<String, List<SearchHit>> hits) {
    }

    private final KeywordSearch keyword;
    private final SemanticSearch semantic;
    private final HybridSearch hybrid;
    private final EmbeddingModel embeddingModel;

    public Evaluator(KeywordSearch keyword, SemanticSearch semantic, HybridSearch hybrid,
                     EmbeddingModel embeddingModel) {
        this.keyword = keyword;
        this.semantic = semantic;
        this.hybrid = hybrid;
        this.embeddingModel = embeddingModel;
    }

    @Override
    public void run(ApplicationArguments args) {
        List<Map<String, String>> queries = CsvReader.read("data/queries.csv");
        NoPrefixIndex noPrefix = NoPrefixIndex.build(embeddingModel);

        Map<String, List<Long>> timings = new LinkedHashMap<>();
        Map<String, BiFunction<String, Integer, List<SearchHit>>> searches = new LinkedHashMap<>();
        searches.put("keyword", keyword::search);
        searches.put("semantic", semantic::search);
        searches.put("hybrid", hybrid::search);
        searches.put("semantic_no_prefix", noPrefix::search);

        List<QueryResult> results = new ArrayList<>();
        for (Map<String, String> q : queries) {
            Map<String, List<SearchHit>> hits = new LinkedHashMap<>();
            searches.forEach((method, search) -> {
                long start = System.nanoTime();
                hits.put(method, search.apply(q.get("query"), TOP));
                timings.computeIfAbsent(method, m -> new ArrayList<>())
                        .add((System.nanoTime() - start) / 1_000_000);
            });
            results.add(new QueryResult(q.get("id"), q.get("group"), q.get("query"),
                    Arrays.asList(q.get("relevant_skus").trim().split("\\s+")), hits));
        }

        Map<String, Map<String, Map<String, Double>>> metrics = new LinkedHashMap<>();
        for (String method : METHODS) {
            Map<String, Map<String, Double>> byGroup = new LinkedHashMap<>();
            for (String group : List.of("exact", "meaning", "code", "all")) {
                List<QueryResult> subset = results.stream()
                        .filter(r -> group.equals("all") || r.group().equals(group))
                        .toList();
                byGroup.put(group, score(subset, method));
            }
            metrics.put(method, byGroup);
        }

        print(metrics, timings);
        write(Path.of("results.json"), results, metrics, timings);
    }

    private Map<String, Double> score(List<QueryResult> subset, String method) {
        double hits = 0;
        double rr = 0;
        for (QueryResult r : subset) {
            int rank = firstRelevantRank(r.hits().get(method), Set.copyOf(r.relevant()));
            hits += (rank > 0 && rank <= 5) ? 1 : 0;
            rr += rank > 0 ? 1.0 / rank : 0;
        }
        Map<String, Double> m = new LinkedHashMap<>();
        m.put("hitAt5", round(hits / subset.size()));
        m.put("mrr", round(rr / subset.size()));
        return m;
    }

    /** Position (1-based) of the first relevant SKU in the top 10, or 0 if none appears. */
    static int firstRelevantRank(List<SearchHit> hits, Set<String> relevant) {
        for (int i = 0; i < Math.min(hits.size(), TOP); i++) {
            if (relevant.contains(hits.get(i).sku())) {
                return i + 1;
            }
        }
        return 0;
    }

    private static double round(double value) {
        return Math.round(value * 1000) / 1000.0;
    }

    private static long median(List<Long> values) {
        List<Long> sorted = values.stream().sorted().toList();
        return sorted.get(sorted.size() / 2);
    }

    private void print(Map<String, Map<String, Map<String, Double>>> metrics, Map<String, List<Long>> timings) {
        StringBuilder sb = new StringBuilder("\n");
        sb.append(String.format("%-20s %-16s %-16s %-16s %-16s %s%n", "search", "exact hit5/mrr",
                "meaning hit5/mrr", "code hit5/mrr", "all hit5/mrr", "median ms"));
        metrics.forEach((method, byGroup) -> {
            sb.append(String.format("%-20s", method));
            byGroup.values().forEach(m -> sb.append(String.format(" %-16s",
                    String.format("%.2f / %.3f", m.get("hitAt5"), m.get("mrr")))));
            sb.append(" ").append(median(timings.get(method))).append('\n');
        });
        log.info(sb.toString());
    }

    private void write(Path file, List<QueryResult> results,
                       Map<String, Map<String, Map<String, Double>>> metrics,
                       Map<String, List<Long>> timings) {
        StringBuilder json = new StringBuilder("{\n  \"metrics\": {");
        String sep = "\n";
        for (var e : metrics.entrySet()) {
            json.append(sep).append("    \"").append(e.getKey()).append("\": {");
            String sep2 = "";
            for (var g : e.getValue().entrySet()) {
                json.append(sep2).append('"').append(g.getKey()).append("\": {\"hitAt5\": ")
                        .append(g.getValue().get("hitAt5")).append(", \"mrr\": ")
                        .append(g.getValue().get("mrr")).append('}');
                sep2 = ", ";
            }
            json.append(", \"medianMillis\": ").append(median(timings.get(e.getKey()))).append('}');
            sep = ",\n";
        }
        json.append("\n  },\n  \"queries\": [");
        sep = "\n";
        for (QueryResult r : results) {
            json.append(sep).append("    {\"id\": \"").append(r.id()).append("\", \"group\": \"")
                    .append(r.group()).append("\", \"query\": \"").append(escape(r.query()))
                    .append("\", \"relevant\": ").append(quoted(r.relevant()));
            for (String method : METHODS) {
                json.append(", \"").append(method).append("\": ")
                        .append(quoted(r.hits().get(method).stream().map(SearchHit::sku).toList()));
            }
            json.append('}');
            sep = ",\n";
        }
        json.append("\n  ]\n}\n");
        try {
            Files.writeString(file, json);
            log.info("Wrote {}", file.toAbsolutePath());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static String quoted(List<String> values) {
        return values.stream().map(v -> "\"" + escape(v) + "\"")
                .collect(java.util.stream.Collectors.joining(", ", "[", "]"));
    }

    private static String escape(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    /** The catalog embedded a second time without the task prefixes, searched in memory. */
    record NoPrefixIndex(EmbeddingModel model, List<String> skus, List<String> names, List<float[]> vectors) {

        static NoPrefixIndex build(EmbeddingModel model) {
            List<Map<String, String>> rows = CsvReader.read("data/products.csv");
            List<float[]> vectors = new ArrayList<>();
            for (int from = 0; from < rows.size(); from += 20) {
                List<String> texts = rows.subList(from, Math.min(from + 20, rows.size())).stream()
                        .map(CatalogLoader::embeddingText)
                        .toList();
                vectors.addAll(model.embed(texts));
            }
            return new NoPrefixIndex(model,
                    rows.stream().map(r -> r.get("sku")).toList(),
                    rows.stream().map(r -> r.get("name")).toList(),
                    vectors);
        }

        List<SearchHit> search(String query, int limit) {
            float[] q = model.embed(query);
            List<SearchHit> hits = new ArrayList<>();
            for (int i = 0; i < skus.size(); i++) {
                hits.add(new SearchHit(skus.get(i), names.get(i), Vectors.cosine(q, vectors.get(i))));
            }
            hits.sort(Comparator.comparingDouble(SearchHit::score).reversed());
            return hits.subList(0, Math.min(limit, hits.size()));
        }
    }
}
