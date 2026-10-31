# PeopleDesk: an HR Policy Assistant That Cites Its Sources

Example project for the howtodoinjava.com article
"How to Build an HR Policy Assistant That Cites Its Sources".

PeopleDesk answers employees' questions from a fictional company's HR policies (offices in India
and Germany) and cites the policy, version and section of every answer. Plain Java code around the
model decides what the model may see and when it may answer:

1. A sensitive-topic check (keyword list, then the model) sends harassment, discrimination,
   health, grievance and legal questions to HR instead of answering them.
2. A metadata filter limits retrieval to the employee's region, employee type and the policy
   version in force on the date of the question.
3. A similarity threshold refuses questions the policies don't cover, without calling the model.
4. The model answers from sections labelled like `[Leave Policy India v3, 1.1]`.
5. A citation check rejects answers whose labels are missing or were not retrieved.

## Versions

- Java 21 (built and run on OpenJDK 25.0.4.1), Maven
- Spring Boot 4.1.2, Spring AI 2.0.2 (`spring-ai-starter-model-ollama`, `spring-ai-rag`,
  `spring-ai-vector-store`, `spring-ai-markdown-document-reader`)
- `SimpleVectorStore` in memory (no database or Docker needed)
- Ollama 0.40.13 with `nomic-embed-text` (embeddings) and `qwen2.5:3b` (answers and the
  sensitive-topic check), temperature 0

## Project layout

| Path | What it is |
|---|---|
| `src/main/resources/policies/` | 11 Markdown policy files (30 numbered sections) with front matter |
| `FrontMatter`, `PolicyLoader` | Front matter parser and section-by-section loading with `MarkdownDocumentReader` |
| `PolicyFilters` | Region, employee type and effective-date filter |
| `SensitiveTopicClassifier`, `SensitiveTopic` | Escalation check |
| `PolicyAssistant` | The pipeline: classify, filter, retrieve, refuse, answer, validate |
| `CitationValidator` | Checks that every cited label was retrieved |
| `AskController` | `POST /api/ask` with `X-Region` and `X-Employee-Type` headers |
| `ThresholdProbe` (`probe` profile) | Best similarity score per question, used to pick the threshold |
| `Evaluation` (`eval` profile) | Runs the 20 labelled questions in `questions.psv` |
| `Demo` (`demo` profile) | The default-threshold trap and the advisor refusal timing |
| `PolicyPipelineTest` | Unit tests that run without a model |

## How to run

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:3b

mvn test                      # 5 tests, no model needed
mvn package -DskipTests
java -jar target/hr-policy-assistant-spring-ai-1.0.0.jar
```

Then ask a question as a full-time employee in India:

```bash
curl -s localhost:8080/api/ask -H 'Content-Type: application/json' \
  -H 'X-Region: IN' -H 'X-Employee-Type: full-time' \
  -d '{"question": "How many days of annual leave do I get per year?"}'
```

Add `"asOf": "2026-02-15"` to the body to ask about a past date.

To reproduce the article's numbers, run `./run-all.sh sample-output`. It runs the threshold probe on
`tuning-questions.psv`, sets the threshold to the midpoint between the weakest answerable and the
strongest unanswerable tuning question, then runs the evaluation and the demo.

## Which model produced the article's numbers

All numbers in the article come from **qwen2.5:3b** (answers and the sensitive-topic check) and
**nomic-embed-text**, on Ollama 0.40.13, on a machine with 2 vCPUs and no GPU, at temperature 0,
on 2026-10-31. The outline originally planned qwen2.5:7b; that model was not run.

Results of the run in `sample-output/` (threshold 0.63 from `tuning-questions.psv`):

| Question type | Correct route | Median time |
|---|---|---|
| 12 answerable | 8/12 answered, all 8 citing the expected section | 11.7 s |
| 4 outside the policies | 4/4 refused | 0.8 s |
| 4 sensitive | 4/4 escalated | 1.2 s |

Of the four missed answerable questions, two were refused (the model replied `NOT_IN_POLICIES`, or
added that marker to its answer) and two were escalated (the classifier replied `GRIEVANCE` to two
notice-period questions). No answer cited another region or a version not in force on the date.

`sample-output/eval-run1.txt` is the first run, before answers containing `NOT_IN_POLICIES` were
rejected (9/12 answered there; one of them carried the marker). Results with a model of a
different size will differ.

Note: in the recorded demo run, the JVM did not exit after printing its output, because
`RetrievalAugmentationAdvisor` starts its own non-daemon thread pool; `timeout` stopped it.
`PeopleDeskApplication` now exits explicitly for the `probe`, `eval` and `demo` profiles.
