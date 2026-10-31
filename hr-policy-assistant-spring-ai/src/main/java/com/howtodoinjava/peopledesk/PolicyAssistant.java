package com.howtodoinjava.peopledesk;

import java.time.LocalDate;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.document.Document;
import org.springframework.ai.ollama.api.OllamaChatOptions;
import org.springframework.ai.rag.Query;
import org.springframework.ai.rag.generation.augmentation.ContextualQueryAugmenter;
import org.springframework.ai.rag.retrieval.search.VectorStoreDocumentRetriever;
import org.springframework.ai.vectorstore.VectorStore;

import com.howtodoinjava.peopledesk.Answer.Route;

public class PolicyAssistant {

    private static final Logger log = LoggerFactory.getLogger(PolicyAssistant.class);

    static final String NOT_IN_POLICIES =
            "I couldn't find this in the HR policies. Please ask HR at %s.";
    static final String ESCALATED =
            "This sounds like something a person in HR should handle. Please contact %s, "
                    + "or use the anonymous ethics line. I have not stored your question.";

    private static final PromptTemplate ANSWER_TEMPLATE = new PromptTemplate("""
            Answer the employee's question using only the policy sections below.
            Each section starts with its label in square brackets.
            After every sentence of your answer, add the label of the section it comes from,
            exactly as written, for example [Expense Policy v1, 3.1].
            If the sections don't answer the question, reply only: NOT_IN_POLICIES
            Keep the answer under 80 words.

            Policy sections:
            {context}

            Question: {query}
            """);

    private final SensitiveTopicClassifier classifier;
    private final VectorStoreDocumentRetriever retriever;
    private final ContextualQueryAugmenter augmenter;
    private final ChatClient chatClient;
    private final String hrContact;

    public PolicyAssistant(SensitiveTopicClassifier classifier, VectorStore vectorStore,
                           ChatClient.Builder builder, PeopleDeskProperties props) {
        this.classifier = classifier;
        this.hrContact = props.hrContact();
        this.retriever = VectorStoreDocumentRetriever.builder()
                .vectorStore(vectorStore)
                .similarityThreshold(props.similarityThreshold())
                .topK(props.topK())
                .build();
        this.augmenter = ContextualQueryAugmenter.builder()
                .promptTemplate(ANSWER_TEMPLATE)
                .documentFormatter(PolicyAssistant::formatWithLabels)
                .build();
        this.chatClient = builder
                .defaultOptions(OllamaChatOptions.builder().temperature(0.0).numPredict(200))
                .build();
    }

    public Answer ask(String question, EmployeeProfile employee, LocalDate asOf) {
        // 1. sensitive topics never reach retrieval or the answer model
        SensitiveTopic topic = classifier.classify(question);
        if (topic != SensitiveTopic.NONE) {
            log.info("Escalated to HR: topic={}, region={}, type={}",
                    topic, employee.region(), employee.employeeType());
            return new Answer(Route.ESCALATED, ESCALATED.formatted(hrContact), Set.of(), List.of(), topic);
        }

        // 2. + 3. retrieve only this employee's sections that are in force on the date
        Query query = Query.builder()
                .text(question)
                .context(Map.of(VectorStoreDocumentRetriever.FILTER_EXPRESSION,
                        PolicyFilters.forEmployee(employee, asOf)))
                .build();
        List<Document> sections = retriever.retrieve(query);
        List<String> retrieved = sections.stream().map(PolicyLoader::label).toList();

        // 4. nothing above the threshold: refuse without calling the model
        if (sections.isEmpty()) {
            return new Answer(Route.REFUSED, NOT_IN_POLICIES.formatted(hrContact), Set.of(), retrieved, topic);
        }

        // 5. answer from the labelled sections
        String prompt = augmenter.augment(query, sections).text();
        String text = chatClient.prompt().user(prompt).call().content();

        // 6. accept the answer only if every citation points to a retrieved section
        Set<String> cited = CitationValidator.citedLabels(text);
        if (text.contains("NOT_IN_POLICIES") || !CitationValidator.isValid(cited, new LinkedHashSet<>(retrieved))) {
            log.warn("Rejected answer, cited={} retrieved={} text={}", cited, retrieved, text);
            return new Answer(Route.REFUSED, NOT_IN_POLICIES.formatted(hrContact), Set.of(), retrieved, topic);
        }
        return new Answer(Route.ANSWERED, text, cited, retrieved, topic);
    }

    static String formatWithLabels(List<Document> sections) {
        return sections.stream()
                .map(doc -> "[" + PolicyLoader.label(doc) + "] " + doc.getText())
                .collect(Collectors.joining("\n\n"));
    }
}
