package com.howtodoinjava.trailgear;

import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;

@Service
public class HybridSearch {

    private final KeywordSearch keyword;
    private final SemanticSearch semantic;
    private final SearchProperties props;

    public HybridSearch(KeywordSearch keyword, SemanticSearch semantic, SearchProperties props) {
        this.keyword = keyword;
        this.semantic = semantic;
        this.props = props;
    }

    public List<SearchHit> search(String query, int limit) {
        List<SearchHit> byWords = keyword.search(query, props.candidates());
        List<SearchHit> byMeaning = semantic.search(query, props.candidates());

        Map<String, Double> scores = new HashMap<>();
        Map<String, String> names = new HashMap<>();
        addRanks(byWords, scores, names);
        addRanks(byMeaning, scores, names);

        // On equal scores, a product that matched the words comes first
        Map<String, Integer> wordRank = new HashMap<>();
        for (int i = 0; i < byWords.size(); i++) {
            wordRank.put(byWords.get(i).sku(), i + 1);
        }
        Comparator<String> order = Comparator
                .comparing((String sku) -> scores.get(sku)).reversed()
                .thenComparing(sku -> wordRank.getOrDefault(sku, Integer.MAX_VALUE))
                .thenComparing(Comparator.naturalOrder());

        return scores.keySet().stream()
                .sorted(order)
                .limit(limit)
                .map(sku -> new SearchHit(sku, names.get(sku), scores.get(sku)))
                .toList();
    }

    private void addRanks(List<SearchHit> hits, Map<String, Double> scores,
                          Map<String, String> names) {
        for (int i = 0; i < hits.size(); i++) {
            SearchHit hit = hits.get(i);
            scores.merge(hit.sku(), 1.0 / (props.rrfK() + i + 1), Double::sum);
            names.putIfAbsent(hit.sku(), hit.name());
        }
    }
}
