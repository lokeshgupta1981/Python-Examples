# Control and Cap LLM Thinking in Ollama With Java

Example project for the howtodoinjava.com article
"How to Control and Cap LLM Thinking in Ollama With Java".

It shows how to switch thinking off and on for a thinking model on Ollama, how to read the
thinking text, how to find the `think` values a model supports with `/api/show`, and how
`num_predict` caps thinking and answer together. A small benchmark measures accuracy,
thinking tokens, answer tokens and time per setting on 12 word problems.

## Versions

- JDK 25, Maven 3.9
- Ollama 0.40.13, model `qwen3:1.7b` (Q4_K_M)
- Spring AI 2.0.2 (`spring-ai-ollama`, used without Spring Boot)
- LangChain4j 1.23.0 (`langchain4j-ollama`)
- Jackson 3.1.7 with `java.net.http.HttpClient` for the raw REST client

## Classes

| Class | What it shows |
|---|---|
| `OllamaThinkingClient` | Streams `/api/chat` with `HttpClient` and counts thinking and answer chunks (one token each); reads `/api/show` |
| `ShowThinkingSupport` | Prints the `thinking` values and default a model reports in `/api/show` |
| `SpringAiThinkingDemo` | `disableThinking()`, `enableThinking()`, the "thinking" metadata key, a 256-token cap and a retry without thinking |
| `LangChain4jThinkingDemo` | `think(true)` and `returnThinking(true)` |
| `WordProblems` | 12 word problems with numeric answers, graded by the last number in the reply |
| `ThinkingBenchmark` | Runs the problems with one setting (`off`, `on`, `on-<num_predict>`) and writes `results/<model>-<setting>.csv` |
| `BenchmarkSummary` | Prints accuracy, mean thinking and answer tokens, truncations and time per CSV file |

## How to run

```bash
ollama pull qwen3:1.7b
mvn -q compile dependency:build-classpath -Dmdep.outputFile=cp.txt
CP=target/classes:$(cat cp.txt)

java -cp $CP com.howtodoinjava.ai.thinking.ShowThinkingSupport qwen3:1.7b
java -cp $CP com.howtodoinjava.ai.thinking.SpringAiThinkingDemo
java -cp $CP com.howtodoinjava.ai.thinking.LangChain4jThinkingDemo

java -cp $CP com.howtodoinjava.ai.thinking.ThinkingBenchmark qwen3:1.7b off
java -cp $CP com.howtodoinjava.ai.thinking.ThinkingBenchmark qwen3:1.7b on 5
java -cp $CP com.howtodoinjava.ai.thinking.ThinkingBenchmark qwen3:1.7b on-256
java -cp $CP com.howtodoinjava.ai.thinking.BenchmarkSummary
```

The optional last argument of `ThinkingBenchmark` limits the number of problems.

## Where the article's numbers come from

All numbers in the article were measured with `qwen3:1.7b` on Ollama 0.40.13, temperature 0,
on a machine with 2 vCPUs (Intel Xeon 2.10 GHz), 7 GB RAM and no GPU, at about 8 generated
tokens per second. The Ollama server was shared with other jobs, but every model run held an
exclusive lock, so runs did not overlap. The `results/` folder holds the CSV files of those runs:

- `off`: problems 1 to 8 (the run was stopped by a 200-second time limit after problem 8)
- `on`: problems 1 to 5 (thinking takes about 2 to 3 minutes per problem on this machine)
- `on-256`: all 12 problems

`results/results-spring-ai.txt` and `results/results-langchain4j.txt` hold the output of the two demos.
On a GPU, the same runs take a fraction of the time; accuracy and token counts can also differ
with other Ollama versions and model builds.

`scripts/think-values-probe.sh` sends `think` as `false`, `true`, `"low"`, `"max"` and `512` to
qwen3 with a 64-token cap; its output is in `results/think-values-probe.txt`.
