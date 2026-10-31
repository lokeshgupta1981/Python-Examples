package com.howtodoinjava.ai.thinking;

import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.Generation;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaChatOptions;

/**
 * Spring AI 2.0.2 without Spring Boot: thinking off, thinking on, and a num_predict cap
 * that cuts the answer off, followed by a retry with thinking off.
 */
public class SpringAiThinkingDemo {

    static final String QUESTION = "Tom is 3 times as old as his son. In 12 years, Tom will be twice as old "
        + "as his son. How old is Tom now?\nReply with the final answer as a number only.";

    public static void main(String[] args) {
        OllamaChatModel chatModel = OllamaChatModel.builder()
            .ollamaApi(OllamaApi.builder().baseUrl("http://localhost:11434").build())
            .options(OllamaChatOptions.builder().model("qwen3:1.7b").temperature(0.0).build())
            .build();

        // 1. Thinking off
        OllamaChatOptions noThinking = OllamaChatOptions.builder()
            .model("qwen3:1.7b")
            .temperature(0.0)
            .disableThinking()
            .build();
        print("think=false", chatModel.call(new Prompt(QUESTION, noThinking)));

        // 2. Thinking on
        OllamaChatOptions thinking = OllamaChatOptions.builder()
            .model("qwen3:1.7b")
            .temperature(0.0)
            .enableThinking()
            .numPredict(4096)
            .build();
        print("think=true", chatModel.call(new Prompt(QUESTION, thinking)));

        // 3. Thinking on with a cap that is too small, then a retry without thinking
        System.out.println(answerWithCap(chatModel, QUESTION, 256));
    }

    static String answerWithCap(OllamaChatModel chatModel, String question, int maxTokens) {
        OllamaChatOptions capped = OllamaChatOptions.builder()
            .model("qwen3:1.7b")
            .temperature(0.0)
            .enableThinking()
            .numPredict(maxTokens)
            .build();
        ChatResponse response = chatModel.call(new Prompt(question, capped));
        print("think=true, num_predict=" + maxTokens, response);

        Generation result = response.getResult();
        if ("length".equals(result.getMetadata().getFinishReason())) {
            OllamaChatOptions direct = capped.mutate().disableThinking().build();
            ChatResponse retry = chatModel.call(new Prompt(question, direct));
            print("retry with think=false", retry);
            return retry.getResult().getOutput().getText();
        }
        return result.getOutput().getText();
    }

    static void print(String label, ChatResponse response) {
        Generation result = response.getResult();
        String thinking = (String) result.getOutput().getMetadata().get("thinking");
        System.out.printf("--- %s%nfinish reason: %s, output tokens: %d%nthinking: %s%nanswer: [%s]%n", label,
            result.getMetadata().getFinishReason(),
            response.getMetadata().getUsage().getCompletionTokens(),
            thinking == null ? "null" : thinking.length() + " characters, starts with \""
                + thinking.strip().replace("\n", " ").substring(0, Math.min(80, thinking.strip().length())) + "\"",
            result.getOutput().getText());
    }

    private SpringAiThinkingDemo() {
    }
}
