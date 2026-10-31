# AI Agent Guardrails in Java: Policies for Tool Calls

Example project for the howtodoinjava.com article "AI Agent Guardrails in Java: Policies for Tool Calls"
(part 2 of the series on running AI agents safely).

An OrderDesk refund agent with three tools (`lookupOrder`, `issueRefund`, `deleteCustomer`). Every tool call
passes a guard layer before the tool runs:

1. Tools offered per role (`RoleAllowList`), and the allow list again as the first gate
2. Argument checks (`RefundArguments`): order belongs to the customer, amount > 0 and <= order total
3. An embedded Cedar policy (`src/main/resources/orderdesk.cedar`, `CedarRefundPolicy`): up to 100 USD alone,
   up to 1,000 USD with an approval, nothing above 1,000 USD; fails closed on errors
4. Human approval bound to a SHA-256 fingerprint of user + tool + arguments (`ApprovalService`), usable once
5. Limits: Spring AI `maxCallsPerTool("issueRefund", 3)` per turn, and a daily spend limit of 500 USD (`SpendLimit`)
6. One audit line per decision (`AuditLog`)

The guard layer (`guard` package) is framework-neutral. Adapters:

- Spring AI: `springai.GuardedToolCallback` wraps each `ToolCallback`; `springai.OrderDeskAgent`
- LangChain4j: `langchain4j.GuardedToolProvider` (a `ToolProvider` plus a wrapping `ToolExecutor`)

## Versions

- Java 25 (tested with OpenJDK 25.0.4.1), Maven 3.9
- Spring AI 2.0.2 (`spring-ai-client-chat`, `spring-ai-ollama`), used without Spring Boot
- Cedar Java 4.11.0 (`com.cedarpolicy:cedar-java`, classifier `uber`)
- LangChain4j 1.23.0
- JUnit 6.1.3, AssertJ 3.27.7

Without Spring Boot's parent POM, `maven.compiler.parameters=true` is needed; otherwise Spring AI passes `null`
for every `@Tool` parameter.

## Run the attack tests (no model needed)

```bash
mvn test
```

24 tests. The tests use `ScriptedChatModel` (Spring AI) and a scripted LangChain4j `ChatModel`, which return
the tool calls an attacker would get out of a model. They run the calls through the real Spring AI tool loop
(`ChatClient` + `ToolCallingAdvisor`) and LangChain4j `AiServices`, and assert that the tool body never ran
and that an audit line was written.

## Run the live scenarios against Ollama

```bash
ollama pull qwen2.5:3b
mvn -q compile exec:java                       # default model qwen2.5:3b
mvn -q compile exec:java -Dexec.args="qwen3:8b"
```

`LiveScenarios` runs six scenarios (small refund, direct injection and order-note injection with and without
the guard, mid-size refund) at temperature 0 and prints the answer, which tools ran, and the audit lines.

The article's live numbers come from qwen2.5:3b on Ollama, CPU only, 2 vCPUs. See LIVE-RESULTS.md.
