package com.howtodoinjava.ai.eval;

import java.time.Duration;
import java.util.List;
import java.util.Map;

import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.metadata.Usage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaChatOptions;

/** Sends one ticket to one setup and records the answer, the tokens and the latency. */
public class TicketClassifier {

    /** JSON schema passed to Ollama as "format", so the model can only answer with valid labels. */
    static final Map<String, Object> ANSWER_SCHEMA = Map.of(
            "type", "object",
            "properties", Map.of(
                    "category", Map.of("type", "string",
                            "enum", List.of("BILLING", "SHIPPING", "RETURNS", "ACCOUNT", "PRODUCT")),
                    "priority", Map.of("type", "string",
                            "enum", List.of("LOW", "NORMAL", "HIGH"))),
            "required", List.of("category", "priority"));

    private final OllamaChatModel chatModel;
    private final Setup setup;

    public TicketClassifier(String baseUrl, Setup setup) {
        this.setup = setup;
        OllamaChatOptions options = OllamaChatOptions.builder()
                .model(setup.model())
                .temperature(setup.temperature())
                .numPredict(setup.maxTokens())
                .format(ANSWER_SCHEMA)
                .disableThinking()
                .build();
        this.chatModel = OllamaChatModel.builder()
                .ollamaApi(OllamaApi.builder().baseUrl(baseUrl).build())
                .options(options)
                .build();
    }

    public ModelAnswer classify(String ticketText) {
        Prompt prompt = new Prompt(List.of(
                new SystemMessage(setup.systemPrompt()),
                new UserMessage(ticketText)));

        long start = System.nanoTime();
        ChatResponse response = chatModel.call(prompt);
        long latencyMillis = (System.nanoTime() - start) / 1_000_000;

        Usage usage = response.getMetadata().getUsage();
        long computeMillis = millis(response.getMetadata().get("prompt-eval-duration"))
                + millis(response.getMetadata().get("eval-duration"));
        return new ModelAnswer(
                response.getResult().getOutput().getText(),
                usage.getPromptTokens(),
                usage.getCompletionTokens(),
                latencyMillis,
                computeMillis);
    }

    private static long millis(Object duration) {
        if (duration instanceof Duration d) {
            return d.toMillis();
        }
        return duration instanceof Number nanos ? nanos.longValue() / 1_000_000 : 0;
    }
}
