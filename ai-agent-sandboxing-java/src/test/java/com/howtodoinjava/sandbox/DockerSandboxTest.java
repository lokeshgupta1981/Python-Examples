package com.howtodoinjava.sandbox;

import com.github.dockerjava.api.model.Capability;
import com.github.dockerjava.api.model.HostConfig;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIf;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;

class DockerSandboxTest {

    @Test
    void containerIsLockedDown() {
        HostConfig config = DockerSandbox.lockedDown("runsc");

        assertThat(config.getNetworkMode()).isEqualTo("none");
        assertThat(config.getReadonlyRootfs()).isTrue();
        assertThat(config.getMemory()).isEqualTo(128L * 1024 * 1024);
        assertThat(config.getMemorySwap()).isEqualTo(128L * 1024 * 1024);
        assertThat(config.getPidsLimit()).isEqualTo(64L);
        assertThat(config.getCapDrop()).containsExactly(Capability.ALL);
        assertThat(config.getSecurityOpts()).containsExactly("no-new-privileges");
        assertThat(config.getRuntime()).isEqualTo("runsc");
    }

    static boolean dockerAvailable() {
        return Files.exists(Path.of("/var/run/docker.sock"));
    }

    @Test
    @EnabledIf("dockerAvailable")
    void containerBlocksNetworkAndCpuLoop() {
        var sandbox = new DockerSandbox("node:24-alpine", null, Duration.ofSeconds(5));

        ExecutionResult network = sandbox.run(
                "require('child_process').execSync('wget -q -T 3 -O - http://example.com').toString()");
        ExecutionResult loop = sandbox.run("while (true) {}");

        assertThat(network.succeeded()).isFalse();
        assertThat(loop.status()).isEqualTo(ExecutionResult.Status.TIMED_OUT);
    }
}
