CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS product (
    sku text PRIMARY KEY,
    name text NOT NULL,
    category text NOT NULL,
    description text NOT NULL,
    attributes text NOT NULL,
    price numeric(8, 2) NOT NULL,
    search_text tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', sku || ' ' || name), 'A') ||
        setweight(to_tsvector('english',
            category || ' ' || description || ' ' || attributes), 'B')
    ) STORED,
    embedding vector(768)
);

CREATE INDEX IF NOT EXISTS product_search_text_idx
    ON product USING gin (search_text);

CREATE INDEX IF NOT EXISTS product_embedding_idx
    ON product USING hnsw (embedding vector_cosine_ops);
