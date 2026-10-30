package com.howtodoinjava.trailgear;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Set;

import org.junit.jupiter.api.Test;

/** Runs without PostgreSQL or Ollama: the two searches are replaced by fixed lists. */
class HybridSearchTest {

    private final SearchProperties props =
            new SearchProperties("search_document:", "search_query:", 768, 20, 60);

    private HybridSearch hybrid(List<SearchHit> byWords, List<SearchHit> byMeaning) {
        KeywordSearch keyword = new KeywordSearch(null) {
            @Override
            public List<SearchHit> search(String query, int limit) {
                return byWords;
            }
        };
        SemanticSearch semantic = new SemanticSearch(null, null, props) {
            @Override
            public List<SearchHit> search(String query, int limit) {
                return byMeaning;
            }
        };
        return new HybridSearch(keyword, semantic, props);
    }

    @Test
    void skuMatchedByWordsWinsTheTie() {
        List<SearchHit> byWords = List.of(new SearchHit("TG-7071", "Trailhead Mosquito Head Net", 0.99));
        List<SearchHit> byMeaning = List.of(
                new SearchHit("TG-5421", "Granite Ultralight Tarp", 0.46),
                new SearchHit("TG-7640", "Granite Down Sleeping Bag", 0.45));

        List<SearchHit> hits = hybrid(byWords, byMeaning).search("TG-7071", 5);

        assertThat(hits).extracting(SearchHit::sku).containsExactly("TG-7071", "TG-5421", "TG-7640");
        assertThat(hits.get(0).score()).isEqualTo(hits.get(1).score()).isEqualTo(1.0 / 61);
    }

    @Test
    void productFoundByBothSearchesMovesUp() {
        List<SearchHit> byWords = List.of(new SearchHit("A", "a", 1), new SearchHit("B", "b", 1));
        List<SearchHit> byMeaning = List.of(new SearchHit("C", "c", 1), new SearchHit("B", "b", 1));

        List<SearchHit> hits = hybrid(byWords, byMeaning).search("q", 5);

        assertThat(hits.get(0).sku()).isEqualTo("B");
        assertThat(hits.get(0).score()).isEqualTo(2.0 / 62);
    }

    @Test
    void firstRelevantRankLooksAtTheTopTen() {
        List<SearchHit> hits = List.of(new SearchHit("X", "x", 1), new SearchHit("Y", "y", 1));
        assertThat(Evaluator.firstRelevantRank(hits, Set.of("Y"))).isEqualTo(2);
        assertThat(Evaluator.firstRelevantRank(hits, Set.of("Z"))).isZero();
    }

    @Test
    void vectorLiteralUsesPgvectorTextFormat() {
        assertThat(Vectors.toLiteral(new float[] {0.12f, -0.03f, 0.08f})).isEqualTo("[0.12,-0.03,0.08]");
    }
}
