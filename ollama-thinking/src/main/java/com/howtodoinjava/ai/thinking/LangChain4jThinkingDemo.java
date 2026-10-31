package com.howtodoinjava.ai.thinking;

import java.time.Duration;

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.ollama.OllamaChatModel;

/** LangChain4j 1.23.0: think(Boolean) switches thinking, returnThinking(Boolean) returns the text. */
public class LangChain4jThinkingDemo {

    public static void main(String[] args) {
        OllamaChatModel model = OllamaChatModel.builder()
            .baseUrl("http://localhost:11434")
            .modelName("qwen3:1.7b")
            .temperature(0.0)
            .think(true)
            .returnThinking(true)
            .timeout(Duration.ofMinutes(5))
            .build();

        ChatResponse response = model.chat(UserMessage.from(SpringAiThinkingDemo.QUESTION));
        AiMessage message = response.aiMessage();

        System.out.println("thinking: " + message.thinking().length() + " characters");
        System.out.println("answer: [" + message.text() + "]");
        System.out.println("finish reason: " + response.finishReason()
            + ", output tokens: " + response.tokenUsage().outputTokenCount());
    }

    private LangChain4jThinkingDemo() {
    }
}
