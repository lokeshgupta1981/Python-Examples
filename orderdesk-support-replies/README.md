# Draft Support Replies From Your Help Docs With AI

Example project for the howtodoinjava.com article
[How to Draft Support Replies From Your Help Docs With AI](https://howtodoinjava.com/?p=48056).

A Spring Boot application drafts replies to customer support tickets from a small help center
(retrieval-augmented generation). Code, not the model, decides when there is nothing to draft,
checks that every citation points to a retrieved article, and adds the article links itself.
An agent edits each draft before it is sent.

## What it shows

- `HelpIndexConfig` reads 12 Markdown help articles with `MarkdownDocumentReader` and indexes them in a
  `SimpleVectorStore` (saved to `help-index.json`, so later starts make no embedding calls).
- `ReplyDrafter` retrieves the top 3 articles above a similarity threshold, stops with "No draft" when none
  matches, asks the chat model for a `DraftReply` (structured output), and checks coverage, citations and links.
- `DraftController` exposes `POST /drafts` and `POST /drafts/{id}/send`, and logs how much the agent changed.
- `EvalRunner` (profile `eval`) runs the 20 labelled tickets in `data/tickets.jsonl` and writes `results.jsonl`;
  mode `thresholds` prints the threshold table from that file without model calls, mode `summary` prints the results.

## Versions

Java 21 (tested with JDK 25), Spring Boot 4.1.2, Spring AI 2.0.2, Ollama with `qwen2.5:7b` (chat) and
`nomic-embed-text` (embeddings).

## How to run

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

mvn package                      # also runs the offline tests (no model needed)
java -jar target/orderdesk-support-replies-1.0.0.jar

curl -s localhost:8080/drafts -H 'Content-Type: application/json' \
  -d '{"ticket": "The password reset email never shows up. I tried twice."}'
```

Evaluation (writes `results.jsonl` and `help-index.json` in the working directory):

```bash
java -jar target/orderdesk-support-replies-1.0.0.jar --spring.profiles.active=eval --orderdesk.eval.mode=full
java -jar target/orderdesk-support-replies-1.0.0.jar --spring.profiles.active=eval --orderdesk.eval.mode=thresholds
```

Add `--orderdesk.eval.limit=3` for a quick test, and `--spring.ai.ollama.chat.model=qwen2.5:3b` for a smaller model.
For the "wrong or unsupported claim" row, create `review.csv` with lines such as `T01,yes` after reading the drafts.
Delete `help-index.json` whenever a help article changes.

## About the numbers in the article

All scores, counts and timings in the article were measured by the author with `qwen2.5:7b` and
`nomic-embed-text` on a shared, CPU-only machine (median 103.8 s per draft with the first prompt, 108.7 s with the final one).

The original help articles and tickets were lost. The files in `src/main/resources/help-center` and
`data/tickets.jsonl` are a rebuilt set with the same ids and the topics the article mentions, so a rerun
gives different scores. Tune the similarity threshold on your own run.

## Smoke test of this rebuild

`mvn test` runs 4 offline tests. A 3-ticket evaluation (T01, T04, T15) with `qwen2.5:3b` on a 2 vCPU, CPU-only machine
drafted T01 and T04 with the expected citation and key fact, and refused T15 through the model's `covered` flag
(median model call 17.1 s). A REST run created a draft citing A04, rejected a blank `finalText` with 400 and logged the send.
These smoke results are not the article's numbers.
