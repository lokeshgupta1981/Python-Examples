package com.howtodoinjava.sandbox;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.async.ResultCallback;
import com.github.dockerjava.api.command.WaitContainerResultCallback;
import com.github.dockerjava.api.model.Capability;
import com.github.dockerjava.api.model.Frame;
import com.github.dockerjava.api.model.HostConfig;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.httpclient5.ApacheDockerHttpClient;

import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Runs the code with Node.js in a throwaway, locked-down container.
 * Needs a running Docker daemon; set runtime to "runsc" to use gVisor.
 */
public class DockerSandbox implements CodeSandbox {

    private final DockerClient docker;
    private final String image;
    private final String runtime;
    private final Duration timeout;

    public DockerSandbox(String image, String runtime, Duration timeout) {
        var config = DefaultDockerClientConfig.createDefaultConfigBuilder().build();
        var httpClient = new ApacheDockerHttpClient.Builder()
                .dockerHost(config.getDockerHost())
                .build();
        this.docker = DockerClientImpl.getInstance(config, httpClient);
        this.image = image;
        this.runtime = runtime;
        this.timeout = timeout;
    }

    @Override
    public String name() {
        return "Docker " + (runtime == null ? "runc" : runtime);
    }

    static HostConfig lockedDown(String runtime) {
        HostConfig hostConfig = HostConfig.newHostConfig()
                .withNetworkMode("none")                        // no network at all
                .withReadonlyRootfs(true)                       // read-only file system
                .withTmpFs(Map.of("/tmp", "rw,noexec,nosuid,size=16m"))
                .withMemory(128L * 1024 * 1024)                 // 128 MB RAM
                .withMemorySwap(128L * 1024 * 1024)             // and no extra swap
                .withNanoCPUs(500_000_000L)                     // half a CPU
                .withPidsLimit(64L)                             // stops fork bombs
                .withCapDrop(Capability.ALL)                    // no Linux capabilities
                .withSecurityOpts(List.of("no-new-privileges"));
        return runtime == null ? hostConfig : hostConfig.withRuntime(runtime);
    }

    @Override
    public ExecutionResult run(String code) {
        String id = docker.createContainerCmd(image)
                .withHostConfig(lockedDown(runtime))
                .withUser("65534:65534")                        // nobody, not root
                .withEnv(List.of())                             // no host secrets
                .withCmd("node", "-e", "console.log(eval(process.argv[1]))", code)
                .exec()
                .getId();
        try {
            docker.startContainerCmd(id).exec();
            Integer exitCode;
            try {
                exitCode = docker.waitContainerCmd(id)
                        .exec(new WaitContainerResultCallback())
                        .awaitStatusCode(timeout.toMillis(), TimeUnit.MILLISECONDS);
            } catch (Exception timedOut) {
                return new ExecutionResult(ExecutionResult.Status.TIMED_OUT, "Killed after " + timeout);
            }
            String logs = logs(id);
            return exitCode == 0
                    ? ExecutionResult.ok(logs)
                    : new ExecutionResult(ExecutionResult.Status.ERROR, "exit " + exitCode + ": " + logs);
        } finally {
            docker.removeContainerCmd(id).withForce(true).exec();
        }
    }

    private String logs(String id) {
        StringBuilder text = new StringBuilder();
        try {
            docker.logContainerCmd(id).withStdOut(true).withStdErr(true)
                    .exec(new ResultCallback.Adapter<Frame>() {
                        @Override
                        public void onNext(Frame frame) {
                            text.append(new String(frame.getPayload()));
                        }
                    }).awaitCompletion(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return text.toString().strip();
    }
}
