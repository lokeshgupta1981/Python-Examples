package com.howtodoinjava.ai.thinking;

/** Prints the think values a model accepts, as reported by Ollama's /api/show. */
public class ShowThinkingSupport {

    public static void main(String[] args) throws Exception {
        OllamaThinkingClient client = new OllamaThinkingClient("http://localhost:11434");
        for (String model : args.length > 0 ? args : new String[] {"qwen3:1.7b", "qwen2.5:3b"}) {
            var thinking = client.thinkingSupport(model);
            System.out.println(model + " -> " + (thinking.isMissingNode() ? "no thinking support" : thinking));
        }
    }

    private ShowThinkingSupport() {
    }
}
