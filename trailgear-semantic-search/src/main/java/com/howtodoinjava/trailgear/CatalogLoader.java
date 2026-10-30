package com.howtodoinjava.trailgear;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Component;

/** Loads data/products.csv into the product table and embeds every product that isn't there yet. */
@Component
@Order(1)
public class CatalogLoader implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(CatalogLoader.class);
    private static final int BATCH_SIZE = 20;
    private static final int MAX_ATTEMPTS = 3;

    private final JdbcClient jdbc;
    private final EmbeddingModel embeddingModel;
    private final SearchProperties props;

    public CatalogLoader(JdbcClient jdbc, EmbeddingModel embeddingModel, SearchProperties props) {
        this.jdbc = jdbc;
        this.embeddingModel = embeddingModel;
        this.props = props;
    }

    @Override
    public void run(ApplicationArguments args) {
        checkDimensions();

        Set<String> loaded = Set.copyOf(
                jdbc.sql("SELECT sku FROM product").query(String.class).list());
        List<Map<String, String>> rows = CsvReader.read("data/products.csv").stream()
                .filter(row -> !loaded.contains(row.get("sku")))
                .toList();
        if (rows.isEmpty()) {
            log.info("Catalog already loaded ({} products)", loaded.size());
            return;
        }

        long start = System.nanoTime();
        for (int from = 0; from < rows.size(); from += BATCH_SIZE) {
            List<Map<String, String>> batch =
                    rows.subList(from, Math.min(from + BATCH_SIZE, rows.size()));
            List<String> texts = batch.stream()
                    .map(row -> props.documentPrefix() + " " + embeddingText(row))
                    .toList();
            List<float[]> vectors = embedWithRetry(texts);
            for (int i = 0; i < batch.size(); i++) {
                insert(batch.get(i), vectors.get(i));
            }
        }
        log.info("Embedded {} products in {} s", rows.size(), (System.nanoTime() - start) / 1_000_000_000);
    }

    private void checkDimensions() {
        int actual = embeddingModel.dimensions();
        if (actual != props.dimensions()) {
            throw new IllegalStateException("The embedding model returns " + actual
                    + " dimensions, but the product.embedding column has " + props.dimensions()
                    + ". Check spring.ai.ollama.embedding.model.");
        }
        log.info("Embedding model returns {} dimensions", actual);
    }

    /** Name, category, description and attributes. The SKU carries no meaning for the model. */
    static String embeddingText(Map<String, String> row) {
        return row.get("name") + ". " + row.get("category") + ". "
                + row.get("description") + " " + row.get("attributes");
    }

    private List<float[]> embedWithRetry(List<String> texts) {
        for (int attempt = 1; ; attempt++) {
            try {
                return embeddingModel.embed(texts);
            } catch (RuntimeException e) {
                if (attempt == MAX_ATTEMPTS) {
                    throw e;
                }
                log.warn("Embedding call failed (attempt {}): {}", attempt, e.getMessage());
                sleep(2_000L * attempt);
            }
        }
    }

    private void insert(Map<String, String> row, float[] vector) {
        jdbc.sql("""
                INSERT INTO product (sku, name, category, description, attributes,
                                     price, embedding)
                VALUES (:sku, :name, :category, :description, :attributes,
                        :price, CAST(:embedding AS vector))
                ON CONFLICT (sku) DO NOTHING
                """)
                .param("sku", row.get("sku"))
                .param("name", row.get("name"))
                .param("category", row.get("category"))
                .param("description", row.get("description"))
                .param("attributes", row.get("attributes"))
                .param("price", new BigDecimal(row.get("price")))
                .param("embedding", Vectors.toLiteral(vector))
                .update();
    }

    private static void sleep(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }
}
