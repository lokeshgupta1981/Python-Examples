package com.howtodoinjava.ai.eval;

import java.util.Map;

import org.springframework.ai.evaluation.EvaluationRequest;
import org.springframework.ai.evaluation.EvaluationResponse;
import org.springframework.ai.evaluation.Evaluator;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Grades an answer in code: it passes only if both labels equal the expected ones. */
public class ExactMatchEvaluator implements Evaluator {

    private static final JsonMapper JSON = JsonMapper.builder().build();

    private final Ticket expected;

    public ExactMatchEvaluator(Ticket expected) {
        this.expected = expected;
    }

    @Override
    public EvaluationResponse evaluate(EvaluationRequest request) {
        String category;
        String priority;
        try {
            JsonNode answer = JSON.readTree(request.getResponseContent());
            category = answer.path("category").asString("");
            priority = answer.path("priority").asString("");
        } catch (RuntimeException e) {
            return new EvaluationResponse(false, 0f, "not valid JSON", Map.of());
        }

        boolean categoryOk = expected.category().equals(category);
        boolean priorityOk = expected.priority().equals(priority);
        String feedback = "expected %s/%s, got %s/%s"
                .formatted(expected.category(), expected.priority(), category, priority);

        return new EvaluationResponse(categoryOk && priorityOk,
                (categoryOk ? 0.5f : 0f) + (priorityOk ? 0.5f : 0f),
                feedback,
                Map.of("categoryOk", categoryOk, "priorityOk", priorityOk));
    }
}
