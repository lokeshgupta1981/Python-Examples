package com.howtodoinjava.ai.replies;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;

import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.document.Document;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

/** Tests for every part that doesn't need a model. */
class OfflineTests {

    private final ReplyProperties props = new ReplyProperties("classpath:help-center/*.md",
            "https://help.orderdesk.example/articles/", "help-index.json", 0.55, 3);

    private final ReplyDrafter drafter =
            new ReplyDrafter(null, props, mock(ChatClient.Builder.class, RETURNS_DEEP_STUBS));

    private static Document article(String id, String title, double score) {
        return Document.builder().id(id).text("text of " + id).score(score)
                .metadata(Map.of("articleId", id, "title", title,
                        "url", "https://help.orderdesk.example/articles/" + id))
                .build();
    }

    @Test
    void readsTwelveArticlesWithIdTitleAndUrl() throws Exception {
        List<Document> articles = new HelpIndexConfig()
                .readArticles(props, new PathMatchingResourcePatternResolver());

        assertThat(articles).hasSize(12);
        Document a04 = articles.stream()
                .filter(d -> "A04".equals(d.getMetadata().get("articleId"))).findFirst().orElseThrow();
        assertThat(a04.getMetadata())
                .containsEntry("title", "How do I reset my password?")
                .containsEntry("url", "https://help.orderdesk.example/articles/reset-password");
    }

    @Test
    void checkAcceptsCitedRetrievedArticleAndAddsLink() {
        List<Document> retrieved = List.of(article("A04", "How do I reset my password?", 0.774));
        DraftReply reply = new DraftReply("Please check your spam folder [A04].", List.of("A04"), true);

        DraftResult result = drafter.check("d1", reply, retrieved);

        assertThat(result.status()).isEqualTo(DraftResult.Status.DRAFT);
        assertThat(result.replyText()).isEqualTo("Please check your spam folder.\n\nHelpful articles:\n"
                + "- How do I reset my password? (https://help.orderdesk.example/articles/A04)");
    }

    @Test
    void checkRejectsUncoveredUncitedForeignCitationAndLinks() {
        List<Document> retrieved = List.of(article("A04", "Reset", 0.774));

        assertThat(drafter.check("d", new DraftReply("", List.of(), false), retrieved).reason())
                .isEqualTo("The model says the articles don't answer this ticket.");
        assertThat(drafter.check("d", new DraftReply("Hi.", List.of(), true), retrieved).reason())
                .isEqualTo("The draft cites no article.");
        assertThat(drafter.check("d", new DraftReply("Hi.", List.of("A09"), true), retrieved).reason())
                .startsWith("The draft cites an article we didn't retrieve");
        assertThat(drafter.check("d", new DraftReply("See www.x.com", List.of("A04"), true), retrieved)
                .reason()).isEqualTo("The draft contains a link.");
    }

    @Test
    void changedPercentIsEditDistanceOverLongerText() {
        assertThat(EditDistance.levenshtein("kitten", "sitting")).isEqualTo(3);
        assertThat(EditDistance.changedPercent("kitten", "sitting")).isEqualTo(43);
        assertThat(EditDistance.changedPercent("", "")).isZero();
        assertThat(EditDistance.changedPercent("", "abc")).isEqualTo(100);
    }
}
