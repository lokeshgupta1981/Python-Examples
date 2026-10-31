package com.howtodoinjava.peopledesk;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;
import java.util.List;
import java.util.Set;

import org.junit.jupiter.api.Test;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.Embedding;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.embedding.EmbeddingRequest;
import org.springframework.ai.embedding.EmbeddingResponse;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.core.io.ClassPathResource;

/** Everything here runs without a model. */
class PolicyPipelineTest {

    private final List<Document> sections = loadAll();

    private static List<Document> loadAll() {
        try {
            return new PolicyLoader().load("classpath:policies/*.md");
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    @Test
    void loadsOneDocumentPerNumberedSectionWithFrontMatter() throws Exception {
        List<Document> leave = new PolicyLoader().loadFile(new ClassPathResource("policies/leave-in-v3.md"));

        assertThat(leave).hasSize(3);
        assertThat(leave.getFirst().getMetadata())
                .containsEntry("policy", "Leave Policy India")
                .containsEntry("version", "3")
                .containsEntry("region", "IN")
                .containsEntry("employee_type", "full-time")
                .containsEntry("effective_from", 20260401)
                .containsEntry("section", "1.1");
        assertThat(PolicyLoader.label(leave.getFirst())).isEqualTo("Leave Policy India v3, 1.1");
        assertThat(sections).hasSize(30);
    }

    @Test
    void filterKeepsOnlyTheEmployeesPoliciesInForce() {
        var deContractor = visible(new EmployeeProfile("DE", "contractor"), LocalDate.of(2026, 10, 31));
        assertThat(deContractor).containsExactlyInAnyOrder(
                "Contractor Terms", "Remote Work Policy", "Expense Policy", "Code of Conduct");

        var inFullTime = visible(new EmployeeProfile("IN", "full-time"), LocalDate.of(2026, 10, 31));
        assertThat(inFullTime).contains("Leave Policy India", "Notice Period Policy India")
                .doesNotContain("Leave Policy Germany", "Contractor Terms");
    }

    @Test
    void dateSelectsTheLeavePolicyVersion() {
        var employee = new EmployeeProfile("IN", "full-time");
        assertThat(versions(employee, LocalDate.of(2026, 3, 31))).containsExactly("2");
        assertThat(versions(employee, LocalDate.of(2026, 4, 1))).containsExactly("3");
    }

    @Test
    void citationsMustPointToRetrievedSections() {
        Set<String> retrieved = Set.of("Leave Policy India v3, 1.1", "Leave Policy India v3, 1.2");

        String good = "You get 21 days of paid annual leave per year [Leave Policy India v3, 1.1].";
        String wrongVersion = "You get 18 days per year [Leave Policy India v2, 1.1].";
        String noCitation = "You get 21 days per year.";

        assertThat(CitationValidator.isValid(CitationValidator.citedLabels(good), retrieved)).isTrue();
        assertThat(CitationValidator.isValid(CitationValidator.citedLabels(wrongVersion), retrieved)).isFalse();
        assertThat(CitationValidator.isValid(CitationValidator.citedLabels(noCitation), retrieved)).isFalse();
    }

    @Test
    void keywordBackstopAndParsing() {
        assertThat(SensitiveTopicClassifier.byKeyword("A colleague keeps bullying me")).isEqualTo(SensitiveTopic.HARASSMENT);
        assertThat(SensitiveTopicClassifier.byKeyword("How many sick days do I get?")).isEqualTo(SensitiveTopic.NONE);
        assertThat(SensitiveTopic.parse("HEALTH")).isEqualTo(SensitiveTopic.HEALTH);
        assertThat(SensitiveTopic.parse("none.")).isEqualTo(SensitiveTopic.NONE);
        assertThat(SensitiveTopic.parse("I am not sure")).isEqualTo(SensitiveTopic.GRIEVANCE);
    }

    // every text gets the same vector, so only the filter decides what comes back
    private static final EmbeddingModel SAME_VECTOR = new EmbeddingModel() {
        @Override
        public EmbeddingResponse call(EmbeddingRequest request) {
            return new EmbeddingResponse(request.getInstructions().stream()
                    .map(t -> new Embedding(new float[] {1f, 0f}, 0)).toList());
        }

        @Override
        public float[] embed(Document document) {
            return new float[] {1f, 0f};
        }
    };

    private List<Document> search(EmployeeProfile employee, LocalDate asOf) {
        SimpleVectorStore store = SimpleVectorStore.builder(SAME_VECTOR).build();
        store.add(sections);
        return store.similaritySearch(SearchRequest.builder().query("any")
                .filterExpression(PolicyFilters.forEmployee(employee, asOf)).topK(100).build());
    }

    private List<String> visible(EmployeeProfile employee, LocalDate asOf) {
        return search(employee, asOf).stream()
                .map(d -> (String) d.getMetadata().get("policy")).distinct().toList();
    }

    private List<String> versions(EmployeeProfile employee, LocalDate asOf) {
        return search(employee, asOf).stream()
                .filter(d -> "Leave Policy India".equals(d.getMetadata().get("policy")))
                .map(d -> (String) d.getMetadata().get("version")).distinct().toList();
    }
}
