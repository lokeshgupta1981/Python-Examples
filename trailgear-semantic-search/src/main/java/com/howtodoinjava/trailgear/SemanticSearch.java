package com.howtodoinjava.trailgear;

import java.util.List;

import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;

@Service
public class SemanticSearch {

    private static final String SQL = """
            SELECT sku, name, 1 - (embedding <=> CAST(:vector AS vector)) AS score
            FROM product
            ORDER BY embedding <=> CAST(:vector AS vector)
            LIMIT :limit
            """;

    private final JdbcClient jdbc;
    private final EmbeddingModel embeddingModel;
    private final SearchProperties props;

    public SemanticSearch(JdbcClient jdbc, EmbeddingModel embeddingModel, SearchProperties props) {
        this.jdbc = jdbc;
        this.embeddingModel = embeddingModel;
        this.props = props;
    }

    public List<SearchHit> search(String query, int limit) {
        float[] vector = embeddingModel.embed(props.queryPrefix() + " " + query);
        return jdbc.sql(SQL)
                .param("vector", Vectors.toLiteral(vector))
                .param("limit", limit)
                .query(SearchHit.class)
                .list();
    }
}
