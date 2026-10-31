package com.howtodoinjava.ai.thinking;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

import com.howtodoinjava.ai.thinking.OllamaThinkingClient.Reply;
import com.howtodoinjava.ai.thinking.WordProblems.Problem;

/**
 * Runs the word problems with one thinking setting and writes one CSV row per problem.
 *
 * Usage: ThinkingBenchmark <model> <setting> [maxProblems]
 * Settings: off, on, on-1024, on-256 (think=true with num_predict 1024 or 256)
 */
public class ThinkingBenchmark {

    record Setting(String name, Object think, Integer numPredict) {
        static Setting parse(String name) {
            return switch (name) {
                case "off" -> new Setting(name, false, 4096);
                case "on" -> new Setting(name, true, 4096);
                default -> {
                    if (!name.startsWith("on-")) {
                        throw new IllegalArgumentException("Unknown setting: " + name);
                    }
                    yield new Setting(name, true, Integer.parseInt(name.substring(3)));
                }
            };
        }
    }

    public static void main(String[] args) throws Exception {
        String model = args[0];
        Setting setting = Setting.parse(args[1]);
        int max = args.length > 2 ? Integer.parseInt(args[2]) : WordProblems.ALL.size();

        OllamaThinkingClient client = new OllamaThinkingClient("http://localhost:11434");
        Path out = Path.of("results", model.replace(':', '_') + "-" + setting.name() + ".csv");
        Files.createDirectories(out.getParent());
        Files.writeString(out, "setting,problem,correct,thinking_tokens,answer_tokens,eval_count,done_reason,millis,answer\n");

        for (Problem problem : WordProblems.ALL.subList(0, max)) {
            Reply reply = client.chat(model, setting.think(), setting.numPredict(), WordProblems.prompt(problem));
            boolean correct = WordProblems.isCorrect(problem, reply.content());
            String answer = reply.content().strip().replace("\n", " ").replace(",", ";");
            if (answer.length() > 60) {
                answer = answer.substring(0, 60) + "...";
            }
            System.out.printf("%-8s #%-2d %-5s thinking=%4d answer=%3d eval=%4d %-6s %6d ms  %s%n",
                setting.name(), problem.id(), correct, reply.thinkingChunks(), reply.contentChunks(),
                reply.evalCount(), reply.doneReason(), reply.millis(), answer);
            Files.writeString(out, String.join(",", setting.name(), String.valueOf(problem.id()), String.valueOf(correct),
                String.valueOf(reply.thinkingChunks()), String.valueOf(reply.contentChunks()),
                String.valueOf(reply.evalCount()), reply.doneReason(), String.valueOf(reply.millis()),
                "\"" + answer + "\"") + "\n", StandardOpenOption.APPEND);
        }
        System.out.println("Wrote " + out);
    }

    private ThinkingBenchmark() {
    }
}
