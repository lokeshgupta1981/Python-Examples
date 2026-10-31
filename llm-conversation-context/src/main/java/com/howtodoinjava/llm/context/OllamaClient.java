package com.howtodoinjava.llm.context;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;

/**
 * A minimal client for Ollama's /api/chat and /api/embed endpoints.
 */
public class OllamaClient {

    private final HttpClient http = HttpClient.newHttpClient();
    private final ObjectMapper json = new ObjectMapper();
    private final String baseUrl;
    private final String model;

    private Integer numCtx;       // null = server default
    private Boolean truncate;     // null = server default (true)
    private String lastRequestBody;

    public OllamaClient(String baseUrl, String model) {
        this.baseUrl = baseUrl;
        this.model = model;
    }

    public OllamaClient withNumCtx(Integer numCtx) {
        this.numCtx = numCtx;
        return this;
    }

    public OllamaClient withTruncate(Boolean truncate) {
        this.truncate = truncate;
        return this;
    }

    public ChatResult chat(List<Message> messages) {
        return chat(messages, 60);
    }

    public ChatResult chat(List<Message> messages, int maxOutputTokens) {
        ObjectNode body = json.createObjectNode();
        body.put("model", model);
        body.put("stream", false);
        if (truncate != null) {
            body.put("truncate", truncate);
        }
        ObjectNode options = body.putObject("options");
        options.put("temperature", 0);
        options.put("num_predict", maxOutputTokens);
        if (numCtx != null) {
            options.put("num_ctx", numCtx);
        }
        ArrayNode array = body.putArray("messages");
        messages.forEach(m -> array.addObject().put("role", m.role()).put("content", m.content()));

        long start = System.nanoTime();
        JsonNode response = post("/api/chat", body);
        long millis = (System.nanoTime() - start) / 1_000_000;

        return new ChatResult(
            response.path("message").path("content").asText().trim(),
            response.path("prompt_eval_count").asInt(),
            response.path("prompt_eval_cached_count").asInt(),
            response.path("eval_count").asInt(),
            millis);
    }

    public float[] embed(String model, String text) {
        ObjectNode body = json.createObjectNode();
        body.put("model", model);
        body.put("input", text);
        JsonNode vector = post("/api/embed", body).path("embeddings").get(0);
        float[] result = new float[vector.size()];
        for (int i = 0; i < result.length; i++) {
            result[i] = (float) vector.get(i).asDouble();
        }
        return result;
    }

    public String lastRequestBody() {
        return lastRequestBody;
    }

    private JsonNode post(String path, ObjectNode body) {
        try {
            lastRequestBody = json.writerWithDefaultPrettyPrinter().writeValueAsString(body);
            HttpRequest request = HttpRequest.newBuilder(URI.create(baseUrl + path))
                .timeout(Duration.ofMinutes(5))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json.writeValueAsString(body)))
                .build();
            HttpResponse<String> response = http.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                throw new OllamaException(response.statusCode(), response.body());
            }
            return json.readTree(response.body());
        } catch (IOException e) {
            throw new IllegalStateException("Ollama call failed", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Interrupted", e);
        }
    }

    public static class OllamaException extends RuntimeException {
        public OllamaException(int status, String body) {
            super("HTTP " + status + ": " + body);
        }
    }
}
