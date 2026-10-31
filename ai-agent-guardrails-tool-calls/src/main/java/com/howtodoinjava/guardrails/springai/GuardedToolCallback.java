package com.howtodoinjava.guardrails.springai;

import java.util.Map;

import org.springframework.ai.chat.model.ToolContext;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.ToolDefinition;
import org.springframework.ai.tool.metadata.ToolMetadata;

import com.howtodoinjava.guardrails.guard.Decision;
import com.howtodoinjava.guardrails.guard.ToolCall;
import com.howtodoinjava.guardrails.guard.ToolGuard;

import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.json.JsonMapper;

/**
 * Wraps a Spring AI tool. Every call passes the guard first; the real tool runs only on ALLOW.
 */
public class GuardedToolCallback implements ToolCallback {

    private static final JsonMapper JSON = JsonMapper.builder().build();

    private final ToolCallback delegate;
    private final ToolGuard guard;

    public GuardedToolCallback(ToolCallback delegate, ToolGuard guard) {
        this.delegate = delegate;
        this.guard = guard;
    }

    @Override
    public ToolDefinition getToolDefinition() {
        return delegate.getToolDefinition();
    }

    @Override
    public ToolMetadata getToolMetadata() {
        return delegate.getToolMetadata();
    }

    @Override
    public String call(String toolInput) {
        return call(toolInput, null);
    }

    @Override
    public String call(String toolInput, ToolContext toolContext) {
        if (toolContext == null || !toolContext.getContext().containsKey("user")) {
            return Decision.deny("context", "no user on this request").toModelText();
        }
        Map<String, Object> ctx = toolContext.getContext();
        Map<String, Object> args;
        try {
            args = JSON.readValue(toolInput, new TypeReference<Map<String, Object>>() {
            });
        } catch (RuntimeException e) {
            return Decision.deny("arguments", "arguments are not a JSON object").toModelText();
        }
        ToolCall call = new ToolCall((String) ctx.get("user"), (String) ctx.get("role"),
                (String) ctx.get("customerId"), getToolDefinition().name(), args);

        Decision decision = guard.evaluate(call);
        if (!decision.allowed()) {
            return decision.toModelText();
        }
        return delegate.call(toolInput, toolContext);
    }
}
