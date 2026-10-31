package com.howtodoinjava.llm.context;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class ConversationDemo {

    static final String OLLAMA = System.getenv().getOrDefault("OLLAMA_URL", "http://localhost:11434");
    static final String MODEL = System.getenv().getOrDefault("CHAT_MODEL", "qwen2.5:3b");
    static final String EMBEDDING_MODEL = "nomic-embed-text";

    static final String SYSTEM_PROMPT =
        "You are a helpful assistant for backend developers. Answer in at most two short sentences.";

    static final List<String> SCRIPT = List.of(
        "My name is Priya and I own the billing service.",
        "Our invoices are created by a nightly batch job. How do I make it safe to run twice?",
        "How should I store money amounts in Java?",
        "Which HTTP status should our API return for a duplicate payment request?",
        "How do I retry a failed call to the payment gateway safely?",
        "What should I log when a payment fails?",
        "How can I test the nightly job on my laptop?",
        "Which metric tells me that the job is getting slower?",
        "How do I add a column to the invoices table without downtime?",
        "What's my name and which service do I own?");

    public static void main(String[] args) throws IOException {
        Set<String> parts = args.length == 0
            ? Set.of("forget", "strategies", "truncation")
            : Set.of(args);
        OllamaClient client = new OllamaClient(OLLAMA, MODEL);

        System.out.printf("Model %s at %s, Java %s%n", MODEL, OLLAMA, System.getProperty("java.version"));
        long warmUp = client.chat(List.of(Message.user("Say OK."))).millis();
        System.out.printf("Warm-up call: %d ms%n", warmUp);

        if (parts.contains("forget")) {
            forget(client);
        }

        Path results = Path.of("results");
        Files.createDirectories(results);
        try (PrintWriter csv = new PrintWriter(Files.newBufferedWriter(results.resolve("turns.csv")))) {
            csv.println("strategy,turn,messages,prompt_tokens,cached_tokens,output_tokens,millis");
            List<String[]> summary = new ArrayList<>();

            if (parts.contains("strategies")) {
                List<ContextStrategy> strategies = List.of(
                    new FullHistory(),
                    new SlidingWindow(3),
                    new TokenBudget(300),
                    new SummarizingHistory(client, 300, 2),
                    new RetrievalHistory(client, EMBEDDING_MODEL, 2, 2));
                for (ContextStrategy strategy : strategies) {
                    summary.add(run(client, strategy, csv, strategy instanceof FullHistory));
                }
            }
            if (parts.contains("truncation")) {
                OllamaClient small = new OllamaClient(OLLAMA, MODEL).withNumCtx(512);
                summary.add(run(small, new FullHistory() {
                    @Override
                    public String name() {
                        return "Full history, num_ctx 512";
                    }
                }, csv, false));
                truncateFalse(small);
            }

            System.out.println();
            System.out.printf("%-28s %-8s %8s %8s %8s %6s %9s%n",
                "Strategy", "Correct", "LastPrm", "SumPrm", "SumCach", "Extra", "Time ms");
            for (String[] row : summary) {
                System.out.printf("%-28s %-8s %8s %8s %8s %6s %9s%n", (Object[]) row);
            }
        }
    }

    static List<Turn> lastTurns = List.of();

    static void forget(OllamaClient client) {
        System.out.println("\n== Two requests without history ==");
        for (String text : List.of(SCRIPT.getFirst(), SCRIPT.getLast())) {
            ChatResult r = client.chat(List.of(Message.system(SYSTEM_PROMPT), Message.user(text)));
            System.out.printf("User: %s%nModel: %s%n", text, r.content());
        }
    }

    static String[] run(OllamaClient client, ContextStrategy strategy, PrintWriter csv, boolean showRequest) {
        System.out.printf("%n== %s ==%n", strategy.name());
        System.out.printf("%4s %8s %7s %7s %7s %8s%n", "Turn", "Messages", "Prompt", "Cached", "Output", "Time ms");

        List<Turn> turns = new ArrayList<>();
        int sumPrompt = 0, sumCached = 0;
        long start = System.nanoTime();
        ChatResult last = null;
        for (String userMessage : SCRIPT) {
            List<Message> messages = strategy.messagesFor(SYSTEM_PROMPT, turns, userMessage);
            last = client.chat(messages);
            turns.add(new Turn(userMessage, last.content(), last));
            sumPrompt += last.promptTokens();
            sumCached += last.cachedTokens();
            System.out.printf("%4d %8d %7d %7d %7d %8d%n", turns.size(), messages.size(),
                last.promptTokens(), last.cachedTokens(), last.outputTokens(), last.millis());
            csv.printf(Locale.ROOT, "\"%s\",%d,%d,%d,%d,%d,%d%n", strategy.name(), turns.size(),
                messages.size(), last.promptTokens(), last.cachedTokens(), last.outputTokens(), last.millis());
            if (showRequest && turns.size() == 2) {
                System.out.println("Request body of turn 2:\n" + client.lastRequestBody());
            }
        }
        long millis = (System.nanoTime() - start) / 1_000_000;
        lastTurns = turns;

        String answer = last.content();
        boolean correct = answer.contains("Priya") && answer.toLowerCase(Locale.ROOT).contains("billing");
        System.out.println("Final answer: " + answer);
        if (strategy instanceof SummarizingHistory s) {
            System.out.println("Summary: " + s.summary());
        }
        if (strategy instanceof RetrievalHistory r) {
            System.out.println("Retrieved turns for the last question: " + r.lastRetrieved());
        }
        return new String[] {strategy.name(), correct ? "yes" : "no",
            String.valueOf(last.promptTokens()), String.valueOf(sumPrompt), String.valueOf(sumCached),
            String.valueOf(strategy.extraCalls()), String.valueOf(millis)};
    }

    static void truncateFalse(OllamaClient small) {
        System.out.println("\n== Same last request, num_ctx 512, truncate=false ==");
        List<Turn> earlier = lastTurns.subList(0, lastTurns.size() - 1);
        List<Message> messages = new FullHistory().messagesFor(SYSTEM_PROMPT, earlier, SCRIPT.getLast());
        try {
            ChatResult r = small.withTruncate(false).chat(messages);
            System.out.println("No error, prompt tokens: " + r.promptTokens());
        } catch (OllamaClient.OllamaException e) {
            System.out.println(e.getMessage());
        }
    }
}
