package com.howtodoinjava.ai.thinking;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.json.JsonMapper;

/**
 * Calls Ollama's /api/chat with streaming on, so that we can count how many
 * chunks (one generated token each) belong to the thinking and to the answer.
 */
public class OllamaThinkingClient {

    private final HttpClient http = HttpClient.newHttpClient();
    private final ObjectMapper json = JsonMapper.builder().build();
    private final String baseUrl;

    public OllamaThinkingClient(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    /** think is Boolean.TRUE, Boolean.FALSE or a level string such as "low". */
    public Reply chat(String model, Object think, Integer numPredict, String prompt)
            throws IOException, InterruptedException {

        Map<String, Object> options = new LinkedHashMap<>();
        options.put("temperature", 0);
        if (numPredict != null) {
            options.put("num_predict", numPredict);
        }
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("model", model);
        body.put("messages", List.of(Map.of("role", "user", "content", prompt)));
        body.put("think", think);
        body.put("stream", true);
        body.put("options", options);

        HttpRequest request = HttpRequest.newBuilder(URI.create(baseUrl + "/api/chat"))
            .timeout(Duration.ofMinutes(10))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(json.writeValueAsString(body)))
            .build();

        long start = System.nanoTime();
        HttpResponse<java.util.stream.Stream<String>> response =
            http.send(request, HttpResponse.BodyHandlers.ofLines());

        if (response.statusCode() != 200) {
            String error = String.join("\n", response.body().toList());
            throw new IllegalStateException("HTTP " + response.statusCode() + ": " + error);
        }

        StringBuilder thinking = new StringBuilder();
        StringBuilder content = new StringBuilder();
        int thinkingChunks = 0;
        int contentChunks = 0;
        int evalCount = 0;
        String doneReason = null;

        Iterator<String> lines = response.body().iterator();
        while (lines.hasNext()) {
            JsonNode chunk = json.readTree(lines.next());
            JsonNode message = chunk.path("message");
            String t = message.path("thinking").asString("");
            String c = message.path("content").asString("");
            if (!t.isEmpty()) {
                thinking.append(t);
                thinkingChunks++;
            }
            if (!c.isEmpty()) {
                content.append(c);
                contentChunks++;
            }
            if (chunk.path("done").asBoolean(false)) {
                evalCount = chunk.path("eval_count").asInt(0);
                doneReason = chunk.path("done_reason").asString(null);
            }
        }
        long millis = (System.nanoTime() - start) / 1_000_000;

        return new Reply(thinking.toString(), content.toString(), thinkingChunks, contentChunks,
            evalCount, doneReason, millis);
    }

    /** Returns the "thinking" object of /api/show, for example {"values":[false,true],"default":true}. */
    public JsonNode thinkingSupport(String model) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder(URI.create(baseUrl + "/api/show"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(json.writeValueAsString(Map.of("model", model))))
            .build();
        String body = http.send(request, HttpResponse.BodyHandlers.ofString()).body();
        return json.readTree(body).path("thinking");
    }

    public record Reply(String thinking, String content, int thinkingChunks, int contentChunks,
                        int evalCount, String doneReason, long millis) {

        public boolean truncated() {
            return "length".equals(doneReason);
        }
    }
}
