package com.howtodoinjava.trailgear;

import java.util.List;

import org.springframework.context.annotation.Profile;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/search")
@Profile("!eval")
public class SearchController {

    private static final int MAX_LIMIT = 20;

    private final KeywordSearch keyword;
    private final SemanticSearch semantic;
    private final HybridSearch hybrid;

    public SearchController(KeywordSearch keyword, SemanticSearch semantic, HybridSearch hybrid) {
        this.keyword = keyword;
        this.semantic = semantic;
        this.hybrid = hybrid;
    }

    @GetMapping("/keyword")
    public List<SearchHit> keyword(@RequestParam String q, @RequestParam(defaultValue = "5") int limit) {
        return keyword.search(q, clamp(limit));
    }

    @GetMapping("/semantic")
    public List<SearchHit> semantic(@RequestParam String q, @RequestParam(defaultValue = "5") int limit) {
        return semantic.search(q, clamp(limit));
    }

    @GetMapping("/hybrid")
    public List<SearchHit> hybrid(@RequestParam String q, @RequestParam(defaultValue = "5") int limit) {
        return hybrid.search(q, clamp(limit));
    }

    private static int clamp(int limit) {
        return Math.max(1, Math.min(limit, MAX_LIMIT));
    }
}
