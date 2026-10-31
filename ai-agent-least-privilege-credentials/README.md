# Least Privilege for AI Agents: Scoped Credentials in Java

Example project for the howtodoinjava.com article "Least Privilege for AI Agents: Scoped Credentials in Java" (part 3 of the series on running AI agents safely).

An OrderDesk support agent (Spring AI) has three tools, and each tool gets its own narrowly scoped credential:

| Tool | Credential | Limited by |
|---|---|---|
| `findOrders` | A database user created per lease by `DatabaseCredentialBroker` (works like Vault's database secrets engine) | `SELECT` on `orders` only, dropped after 5 minutes |
| `cancelOrder` | The signed-in user's token, exchanged with RFC 8693 token exchange (Spring Security `RestClientTokenExchangeTokenResponseClient`) | Audience `orders-api`, scope `orders:cancel`, subject = the user, 5 minutes |
| `sendReport` | Its own client-credentials token (Spring Security `RestClientClientCredentialsTokenResponseClient`) | Audience `reports-api`, scope `reports:send`, 5 minutes |

For contrast, `OrderDesk.sharedKey(...)` wires all three tools to the database owner account and one admin token.

Everything runs inside the JVM, no containers needed:

- H2 in-memory database with real users and `GRANT`s (stands in for PostgreSQL)
- `AuthServer`: a small OAuth 2.0 server (client_credentials and token exchange grants, RS256 JWTs) on the JDK HTTP server (stands in for Keycloak / Spring Authorization Server)
- `OrdersApi` and `ReportsApi`: resource servers that check signature, issuer, expiry, audience and scope; the Orders API also checks that the order belongs to the token's subject

## Versions

- Java 25 (tested on OpenJDK 25)
- Spring AI 2.0.2 (`spring-ai-client-chat`, `spring-ai-ollama`)
- Spring Security 7.1.2 (`spring-security-oauth2-client`, `spring-security-oauth2-jose`)
- Nimbus JOSE+JWT 10.10
- H2 2.5.252
- JUnit 6.1.3, AssertJ 3.27.7, Maven Surefire 3.6.1

## How to run

Attack tests (deterministic, no model needed):

```bash
mvn test
```

- `ScopedCredentialsAttackTest` (15 tests): each attack uses the credential a tool really holds; all fail.
- `SharedKeyAttackTest` (3 tests): the same attacks succeed with one shared key.
- `NoSecretsReachTheModelTest` (4 tests): a scripted, "hijacked" model calls the tools; the test searches everything sent to the model for secrets and tokens, and compares Spring AI's default tool error handling with `SafeToolErrors`.

Side-by-side attack table for both setups:

```bash
mvn compile exec:java
```

Decoded claims of the tokens each tool receives:

```bash
mvn compile exec:java -Dexec.mainClass=com.howtodoinjava.leastprivilege.ShowTokens
```

Live conversations against a local Ollama model (needs Ollama on `localhost:11434` with the model pulled):

```bash
mvn compile exec:java -Dexec.mainClass=com.howtodoinjava.leastprivilege.LiveScenarios -Dexec.args="qwen2.5:3b"
```

## Which model produced the article's numbers

The attack results and token claims in the article come from the deterministic programs and tests above; no model is involved. The live-conversation results in section 5 of the article come from `LiveScenarios` with qwen2.5:3b on Ollama, temperature 0, `num_predict` 200, on a CPU-only machine with 2 vCPUs. Small models vary; your tool calls and answers may differ.
