package com.howtodoinjava.peopledesk;

import java.util.List;
import java.util.Locale;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.ollama.api.OllamaChatOptions;

public class SensitiveTopicClassifier {

    private static final Logger log = LoggerFactory.getLogger(SensitiveTopicClassifier.class);

    private static final String SYSTEM = """
            You route questions that employees send to an HR policy assistant.
            Reply with exactly one word from this list:
            HARASSMENT - the employee reports or describes harassment, bullying or sexual misconduct
            DISCRIMINATION - the employee reports unfair treatment because of gender, religion, age, origin, disability or similar
            HEALTH - the employee discloses their own medical or mental health condition
            GRIEVANCE - the employee complains about their manager, a colleague, pay or a decision
            LEGAL - the employee asks for legal advice or mentions a lawyer, lawsuit or the police
            NONE - a general question about a policy, such as leave days, expenses, notice periods or remote work
            Questions about how many sick days or parental leave days exist are NONE.
            """;

    // backstop: plain code catches the obvious cases even if the model misses them
    private static final Map<SensitiveTopic, List<String>> KEYWORDS = Map.of(
            SensitiveTopic.HARASSMENT, List.of("harass", "bully", "bullied", "inappropriate touch", "sexual"),
            SensitiveTopic.DISCRIMINATION, List.of("discriminat", "racist", "because i am a woman"),
            SensitiveTopic.HEALTH, List.of("diagnosed", "depression", "mental health", "therapy"),
            SensitiveTopic.LEGAL, List.of("lawyer", "lawsuit", "sue the company", "police"));

    private final ChatClient chatClient;

    public SensitiveTopicClassifier(ChatClient.Builder builder) {
        this.chatClient = builder
                .defaultSystem(SYSTEM)
                .defaultOptions(OllamaChatOptions.builder().temperature(0.0).numPredict(5))
                .build();
    }

    public SensitiveTopic classify(String question) {
        SensitiveTopic byKeyword = byKeyword(question);
        if (byKeyword != SensitiveTopic.NONE) {
            return byKeyword;
        }
        String reply = chatClient.prompt().user(question).call().content();
        log.info("Classifier reply: {}", reply);
        return SensitiveTopic.parse(reply);
    }

    static SensitiveTopic byKeyword(String question) {
        String text = question.toLowerCase(Locale.ROOT);
        for (var entry : KEYWORDS.entrySet()) {
            if (entry.getValue().stream().anyMatch(text::contains)) {
                return entry.getKey();
            }
        }
        return SensitiveTopic.NONE;
    }
}
