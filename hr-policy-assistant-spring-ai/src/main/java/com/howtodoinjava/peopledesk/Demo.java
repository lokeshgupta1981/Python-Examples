package com.howtodoinjava.peopledesk;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.ChatClientResponse;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.ai.document.Document;
import org.springframework.ai.ollama.api.OllamaChatOptions;
import org.springframework.ai.rag.advisor.RetrievalAugmentationAdvisor;
import org.springframework.ai.rag.generation.augmentation.ContextualQueryAugmenter;
import org.springframework.ai.rag.retrieval.search.VectorStoreDocumentRetriever;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

/** Shows the two refusal traps: the default threshold, and the advisor that still calls the model. */
@Component
@Profile("demo")
public class Demo implements CommandLineRunner {

    private final SimpleVectorStore store;
    private final ChatClient.Builder builder;
    private final SensitiveTopicClassifier classifier;
    private final PeopleDeskProperties props;

    public Demo(SimpleVectorStore store, ChatClient.Builder builder,
                SensitiveTopicClassifier classifier, PeopleDeskProperties props) {
        this.store = store;
        this.builder = builder;
        this.classifier = classifier;
        this.props = props;
    }

    @Override
    public void run(String... args) {
        var employee = new EmployeeProfile("IN", "full-time");
        String question = "Can I bring my dog to the office?";

        // Trap 1: the default threshold (0.0) accepts every section
        var defaultRetriever = VectorStoreDocumentRetriever.builder().vectorStore(store).build();
        List<Document> docs = defaultRetriever.retrieve(org.springframework.ai.rag.Query.builder()
                .text(question)
                .context(Map.of(VectorStoreDocumentRetriever.FILTER_EXPRESSION,
                        PolicyFilters.forEmployee(employee, LocalDate.of(2026, 10, 31))))
                .build());
        System.out.println("Default threshold retrieved " + docs.size() + " sections: "
                + docs.stream().map(d -> "%s (%.3f)".formatted(PolicyLoader.label(d), d.getScore())).toList());

        var loose = new PolicyAssistant(classifier, store, builder.clone(),
                new PeopleDeskProperties(0.0, props.topK(), props.hrContact()));
        timed("Threshold 0.0 answer", () -> loose.ask(question, employee, LocalDate.of(2026, 10, 31)).toString());

        // Trap 2: RetrievalAugmentationAdvisor calls the model even when nothing is retrieved
        var advisor = RetrievalAugmentationAdvisor.builder()
                .documentRetriever(VectorStoreDocumentRetriever.builder()
                        .vectorStore(store)
                        .similarityThreshold(props.similarityThreshold())
                        .topK(props.topK())
                        .build())
                .queryAugmenter(ContextualQueryAugmenter.builder()
                        .emptyContextPromptTemplate(new PromptTemplate(
                                "Reply only: I couldn't find this in the HR policies. Please ask HR at "
                                        + props.hrContact() + "."))
                        .build())
                .build();
        ChatClient ragClient = builder.clone()
                .defaultOptions(OllamaChatOptions.builder().temperature(0.0).numPredict(200))
                .defaultAdvisors(advisor)
                .build();
        timed("Advisor refusal", () -> {
            ChatClientResponse response = ragClient.prompt().user(question)
                    .advisors(a -> a.param(VectorStoreDocumentRetriever.FILTER_EXPRESSION,
                            PolicyFilters.forEmployee(employee, LocalDate.of(2026, 10, 31))))
                    .call().chatClientResponse();
            Object context = response.context().get(RetrievalAugmentationAdvisor.DOCUMENT_CONTEXT);
            return "documents=" + context + ", reply=" + response.chatResponse().getResult().getOutput().getText();
        });
    }

    private static void timed(String name, java.util.function.Supplier<String> call) {
        long start = System.nanoTime();
        String result = call.get();
        System.out.printf("%s (%.1fs): %s%n", name, (System.nanoTime() - start) / 1e9, result);
    }
}
