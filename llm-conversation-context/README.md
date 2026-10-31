# LLM Conversation Context in Plain Java

Example project for the howtodoinjava.com article
"How to Maintain Conversation Context Across LLM API Requests".

It talks to Ollama's `/api/chat` endpoint with `java.net.http.HttpClient` and Jackson (no AI framework)
and runs one scripted ten-turn conversation with five ways of choosing the history to send:

| Class | Strategy |
|---|---|
| `FullHistory` | Every earlier turn, every time |
| `SlidingWindow` | The last N turns |
| `TokenBudget` | As many recent turns as fit into a token budget, measured with Ollama's own token counts |
| `SummarizingHistory` | Older turns replaced by a short summary written by the same model |
| `RetrievalHistory` | The last turns plus the older turns most similar to the new question (embeddings) |

For every turn it prints the number of messages sent, prompt tokens, prompt tokens read from Ollama's cache,
output tokens and the time of the call, and writes the same rows to `results/turns.csv`.
It also shows the model forgetting without history, Ollama's silent truncation with `num_ctx` 512,
and the error returned with `"truncate": false`.

## Versions

- Java 21 or later (`maven.compiler.release` 21); the article's run used OpenJDK 25.0.4.1 and Maven 3.9.11
- Jackson 2.20.0
- Ollama 0.40.13 with `qwen2.5:3b` (chat) and `nomic-embed-text` (embeddings)

## How to Run

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
mvn compile exec:java
```

Run only some parts with arguments: `mvn compile exec:java -Dexec.args="forget"`
(`forget`, `strategies`, `truncation`). `OLLAMA_URL` and `CHAT_MODEL` environment variables override
the server address and the chat model.

## Numbers in the Article

The article's numbers come from one run with `qwen2.5:3b` (temperature 0, at most 60 output tokens per answer)
on a CPU-only machine with 2 vCPUs (Intel Xeon at 2.10 GHz) and 7 GB of RAM. The full log of that run is in
`results/run.log`, the per-turn numbers in `results/turns.csv`. Answers and timings differ between models,
machines and Ollama versions.
