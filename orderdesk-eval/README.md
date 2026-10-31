# OrderDesk Eval: Measuring LLM Accuracy vs Cost on Your Own Tasks

Example project for the howtodoinjava.com article
"How to Measure LLM Accuracy vs Cost on Your Own Tasks".

It classifies 40 hand-labelled support tickets of a fictional shop ("OrderDesk") into a
category and a priority, grades every answer in code with a custom Spring AI `Evaluator`,
and compares several setups (model and prompt) by accuracy, tokens, latency and cost per
correct answer.

## What it shows

- `src/main/resources/tickets.jsonl`: the labelled test set (40 synthetic tickets, no personal data).
- `Setup`, `Prompts`: the setups we compare (model, system prompt, temperature, max tokens).
- `TicketClassifier`: calls Ollama through Spring AI's `OllamaChatModel` with a JSON schema
  as `format`, and records prompt tokens, output tokens, latency and Ollama's compute time.
- `ExactMatchEvaluator`: a Spring AI `Evaluator` that passes only when both labels match.
- `EvalRunner`: runs the chosen setups once on the whole test set and appends one line per
  call to `results/raw-results.csv`.
- `Report`: reads the CSV and prints accuracy with a 95% margin of error, per-field accuracy,
  tokens, latency percentiles, tokens and compute seconds per correct answer, run-to-run
  changes and a paired comparison between setups.

## Versions

- Java 25 (OpenJDK 25.0.4.1), Maven 3.9
- Spring AI 2.0.2 (`spring-ai-ollama`, no Spring Boot needed)
- Ollama 0.40.13 with `qwen2.5:3b` and `qwen3:1.7b` (both Q4_K_M)

## How to run

```bash
ollama pull qwen2.5:3b
ollama pull qwen3:1.7b

mvn compile
mvn dependency:build-classpath -Dmdep.outputFile=cp.txt
CP=target/classes:$(cat cp.txt)

# run 1 of every setup, then a second run of chosen setups
java -cp $CP com.howtodoinjava.ai.eval.EvalRunner 1
java -cp $CP com.howtodoinjava.ai.eval.EvalRunner 2 "qwen3:1.7b zero-shot"

# print the tables from results/raw-results.csv
java -cp $CP com.howtodoinjava.ai.eval.Report
```

Set `OLLAMA_URL` if Ollama is not at `http://localhost:11434`. Delete
`results/raw-results.csv` to start a fresh comparison.

## Where the article's numbers come from

All numbers in the article were measured with this project on 2026-10-31 with `qwen2.5:3b`
and `qwen3:1.7b` (Q4_K_M, Ollama 0.40.13) on a CPU-only machine (2 vCPUs, Intel Xeon at
2.10 GHz, 7 GB RAM). Each setup ran once over the 40 tickets (run 1). The Ollama server was
shared with other jobs: the `qwen2.5:3b` runs had the server mostly to themselves, the
`qwen3:1.7b` runs did not, so their latency and compute times are not comparable. Token
counts and accuracy do not depend on load. The raw results are in `results/raw-results.csv`.
