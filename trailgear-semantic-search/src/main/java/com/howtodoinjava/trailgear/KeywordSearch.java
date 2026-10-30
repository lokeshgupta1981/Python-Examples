package com.howtodoinjava.trailgear;

import java.util.List;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;

@Service
public class KeywordSearch {

    private static final String SQL = """
            SELECT sku, name, ts_rank(search_text, q) AS score
            FROM product, websearch_to_tsquery('english', :query) AS q
            WHERE search_text @@ q
            ORDER BY score DESC, sku
            LIMIT :limit
            """;

    private final JdbcClient jdbc;

    public KeywordSearch(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public List<SearchHit> search(String query, int limit) {
        return jdbc.sql(SQL)
                .param("query", query)
                .param("limit", limit)
                .query(SearchHit.class)
                .list();
    }
}
