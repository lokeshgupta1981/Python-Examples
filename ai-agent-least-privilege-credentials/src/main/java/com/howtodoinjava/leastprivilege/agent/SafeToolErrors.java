package com.howtodoinjava.leastprivilege.agent;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;

import org.springframework.ai.tool.execution.ToolExecutionException;
import org.springframework.ai.tool.execution.ToolExecutionExceptionProcessor;

/**
 * Turns a failed tool call into a short message without any detail from the exception.
 * The details stay on our side, under an error id that support can look up.
 */
public class SafeToolErrors implements ToolExecutionExceptionProcessor {

    public record LoggedError(String id, String tool, Throwable error) {
    }

    private final List<LoggedError> log = new CopyOnWriteArrayList<>();

    @Override
    public String process(ToolExecutionException exception) {
        String id = UUID.randomUUID().toString().substring(0, 8);
        String tool = exception.getToolDefinition().name();
        log.add(new LoggedError(id, tool, exception.getCause()));
        return "The " + tool + " tool failed (error id " + id + "). Tell the customer to try again later.";
    }

    public List<LoggedError> log() {
        return List.copyOf(log);
    }
}
