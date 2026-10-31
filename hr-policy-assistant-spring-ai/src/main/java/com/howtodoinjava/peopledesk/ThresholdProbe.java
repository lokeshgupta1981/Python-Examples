package com.howtodoinjava.peopledesk;

import java.util.List;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

/** Prints the best similarity score per question, to choose the refusal threshold. Embeddings only. */
@Component
@Profile("probe")
public class ThresholdProbe implements ApplicationRunner {

    private final SimpleVectorStore store;

    public ThresholdProbe(SimpleVectorStore store) {
        this.store = store;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        List<String> files = args.getNonOptionArgs().isEmpty()
                ? List.of("tuning-questions.psv") : args.getNonOptionArgs();
        for (String file : files) {
            probe(file);
        }
    }

    private void probe(String file) throws Exception {
        for (LabelledQuestion q : LabelledQuestion.load(file)) {
            if (q.expectedRoute() == Answer.Route.ESCALATED) {
                continue;
            }
            List<Document> top = store.similaritySearch(SearchRequest.builder()
                    .query(q.question())
                    .filterExpression(PolicyFilters.forEmployee(q.employee(), q.asOf()))
                    .similarityThreshold(0.0)
                    .topK(3)
                    .build());
            StringBuilder line = new StringBuilder("%s %-8s".formatted(q.id(), q.expectedRoute()));
            for (Document d : top) {
                line.append(" | %.3f %s".formatted(d.getScore(), PolicyLoader.label(d)));
            }
            System.out.println(line);
        }
    }
}
