# Semantic Search for a Product Catalog in Spring Boot

Example project for the howtodoinjava.com article "Semantic Search for a Product Catalog in Spring Boot".

It adds three searches to one PostgreSQL `product` table of a made-up outdoor shop called TrailGear:

- **Keyword search**: PostgreSQL full-text search (`tsvector`, `websearch_to_tsquery`, `ts_rank`, GIN index).
- **Semantic search**: embeddings from `nomic-embed-text` in Ollama, stored and searched with pgvector (HNSW index, cosine distance).
- **Hybrid search**: both top-20 lists merged with reciprocal rank fusion (RRF, k = 60), with a tie-break that favours word matches.

An evaluator runs 30 labelled queries (10 exact product terms, 10 meaning-only descriptions, 10 SKU codes) and reports hit@5 and MRR for each search.

## Versions

- Java 21 or later (built and run with OpenJDK 25.0.4.1)
- Spring Boot 4.1.2, Spring AI 2.0.2 (only the Ollama embedding model)
- PostgreSQL 12+ with pgvector 0.5.0+ (tested on PostgreSQL 16.15 with pgvector 0.6.0)
- Ollama with `nomic-embed-text` (768 dimensions)

## How to run

```bash
ollama pull nomic-embed-text

docker run -d --name trailgear-db -p 5432:5432 \
  -e POSTGRES_USER=trailgear -e POSTGRES_PASSWORD=change-me \
  -e POSTGRES_DB=trailgear pgvector/pgvector:pg18-trixie

export SPRING_DATASOURCE_PASSWORD=change-me
mvn spring-boot:run
```

On the first start, `CatalogLoader` embeds the 200 products in `src/main/resources/data/products.csv` (batches of 20) and inserts them. Later starts make no model calls. Then:

```bash
curl "http://localhost:8080/search/keyword?q=something+to+keep+my+feet+warm+on+a+winter+hike"
curl "http://localhost:8080/search/semantic?q=something+to+keep+my+feet+warm+on+a+winter+hike"
curl "http://localhost:8080/search/hybrid?q=TG-7071"
```

Each endpoint takes `q` and an optional `limit` (default 5, at most 20).

Evaluation (no web server; writes `results.json`):

```bash
mvn -q package -DskipTests
java -jar target/trailgear-semantic-search-1.0.0.jar --spring.profiles.active=eval
```

Unit tests (`mvn test`) need neither PostgreSQL nor Ollama.

If PostgreSQL rejects the connection with `invalid value for parameter "TimeZone": "Asia/Calcutta"`, the JVM's default time zone name is an old alias; start Java with `-Duser.timezone=Asia/Kolkata` (or your zone's current name).

## Which numbers are in the article

The results table in the article (hybrid hit@5 0.97, keyword 0.67, semantic 0.63, embedding time 99 s, median latencies 218 ms and 244 ms) come from the author's original run with `nomic-embed-text` in Ollama on PostgreSQL 16 with pgvector 0.6.0. The original data files of that run were not preserved.

This folder rebuilds the project from the article. `products.csv` and `queries.csv` were recreated with the same structure (40 product types x 5 variants, 3 groups of 10 queries) and the SKUs the article quotes, so the evaluator's numbers differ slightly. A run of this rebuilt version on 2026-10-31 (OpenJDK 25, PostgreSQL 16.15, pgvector 0.6.0, `nomic-embed-text` on a shared, CPU-only Ollama with 2 vCPU) gave:

| Search | Exact terms hit@5 / MRR | Meaning only hit@5 / MRR | SKU codes hit@5 / MRR | All 30 hit@5 / MRR |
|---|---|---|---|---|
| Keyword | 1.00 / 1.000 | 0.00 / 0.000 | 1.00 / 1.000 | 0.67 / 0.667 |
| Semantic | 1.00 / 1.000 | 1.00 / 0.950 | 0.00 / 0.000 | 0.67 / 0.650 |
| Hybrid | 1.00 / 1.000 | 1.00 / 0.950 | 1.00 / 1.000 | 1.00 / 0.983 |
| Semantic without prefixes | 1.00 / 1.000 | 0.90 / 0.792 | 0.00 / 0.000 | 0.63 / 0.597 |

Embedding the 200 products took 146 s; median latency was 1 ms (keyword), 525 ms (semantic) and 548 ms (hybrid) on that shared server. The full output is in `sample-output/`.
