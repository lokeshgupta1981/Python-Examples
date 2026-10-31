# AI Agent Sandboxing in Java

Example project for the howtodoinjava.com article "AI Agent Sandboxing in Java: Run LLM-Generated Code Safely".

An OrderDesk agent gets a code tool, `runJavaScript(code)`, that runs model-written JavaScript over order data.
The tool talks to a `CodeSandbox` interface with these executors:

| Class | What it is |
|---|---|
| `UnsafeExecutor` | GraalJS with `allowAllAccess(true)`. For contrast only, never use it. |
| `ConstrainedSandbox` | GraalVM `SandboxPolicy.CONSTRAINED`, a statement limit and a wall-clock timeout. Shares the host heap. |
| `UntrustedSandbox` | GraalVM `SandboxPolicy.UNTRUSTED` in a separate isolate with CPU time, heap, thread, AST depth and output limits. |
| `DockerSandbox` | A throwaway `node:24-alpine` container started with docker-java: no network, read-only root, 128 MB, half a CPU, 64 processes, no capabilities, no-new-privileges, optional gVisor (`runsc`). |

`Attack` holds six malicious snippets (read an env secret, read a file, open a socket, start a process, endless loop, memory bomb).

## Versions

- OpenJDK 25.0.4.1 (any JDK 25 works; the code uses `maven.compiler.release` 25)
- GraalVM Polyglot API, `js-community` and `js-isolate-community` 25.4.4.1.1 (Maven Central, no GraalVM JDK needed)
- docker-java 3.7.1, Spring AI `spring-ai-model` 2.0.2 (for the `@Tool` wrapper), Jackson 3.2.4
- JUnit 6.1.3, AssertJ 3.27.7, Maven 3.9

`js-isolate-community` ships native isolates for linux-amd64, linux-aarch64, darwin-aarch64 and windows-amd64 only.

## How to run

```bash
# all tests (20; the Docker attack test is skipped when /var/run/docker.sock is missing)
mvn test

# attack matrix: every attack against every in-process executor, one fresh JVM per case
mvn -q compile dependency:build-classpath -Dmdep.outputFile=cp.txt
./run-attack-matrix.sh

# the CONSTRAINED memory bomb against the host heap, and the same bomb in the UNTRUSTED isolate
java -Xmx512m -cp "target/classes:$(cat cp.txt)" com.howtodoinjava.sandbox.SharedHeapDemo
java -Xmx512m -cp "target/classes:$(cat cp.txt)" com.howtodoinjava.sandbox.SharedHeapDemo untrusted

# per-call cost of each executor
java -cp "target/classes:$(cat cp.txt)" com.howtodoinjava.sandbox.StartupBenchmark untrusted

# the agent demo: needs Ollama on localhost:11434 with the model pulled (default qwen2.5:3b, or -Dmodel=...)
DB_PASSWORD=s3cr3t-from-env java -cp "target/classes:$(cat cp.txt)" com.howtodoinjava.sandbox.AgentDemo
```

Add `--enable-native-access=ALL-UNNAMED` to the `java` commands to silence the JDK's native-access warning.

## Where the article's numbers come from

- All attack results, heap numbers and timings were measured on OpenJDK 25.0.4.1, Linux, 2 vCPU, CPU only, on a shared machine. Timings show orders of magnitude only.
- The agent demo output in section 1 was produced by `qwen2.5:3b` running locally in Ollama (temperature 0), one run.
- `DockerSandbox` was not run: the build machine had no Docker daemon. Its configuration is checked by `DockerSandboxTest.containerIsLockedDown`.
