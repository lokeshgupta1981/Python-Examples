package com.howtodoinjava.guardrails.langchain4j;

import java.lang.reflect.Method;
import java.util.Map;
import java.util.Set;

import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.agent.tool.ToolExecutionRequest;
import dev.langchain4j.agent.tool.ToolSpecification;
import dev.langchain4j.agent.tool.ToolSpecifications;
import dev.langchain4j.invocation.InvocationContext;
import dev.langchain4j.invocation.InvocationParameters;
import dev.langchain4j.service.tool.DefaultToolExecutor;
import dev.langchain4j.service.tool.ToolExecutionResult;
import dev.langchain4j.service.tool.ToolExecutor;
import dev.langchain4j.service.tool.ToolProvider;
import dev.langchain4j.service.tool.ToolProviderRequest;
import dev.langchain4j.service.tool.ToolProviderResult;

import com.howtodoinjava.guardrails.guard.Decision;
import com.howtodoinjava.guardrails.guard.RoleAllowList;
import com.howtodoinjava.guardrails.guard.ToolCall;
import com.howtodoinjava.guardrails.guard.ToolGuard;

import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.json.JsonMapper;

/**
 * Offers each request only the tools of its role, and wraps every tool in the guard.
 * The user, role and customer come from InvocationParameters, which the model never sees.
 */
public class GuardedToolProvider implements ToolProvider {

    private static final JsonMapper JSON = JsonMapper.builder().build();

    private final Object toolsObject;
    private final RoleAllowList allowList;
    private final ToolGuard guard;

    public GuardedToolProvider(Object toolsObject, RoleAllowList allowList, ToolGuard guard) {
        this.toolsObject = toolsObject;
        this.allowList = allowList;
        this.guard = guard;
    }

    @Override
    public ToolProviderResult provideTools(ToolProviderRequest request) {
        Set<String> allowed = allowList.toolsFor(request.invocationParameters().get("role"));
        ToolProviderResult.Builder result = ToolProviderResult.builder();
        for (Method method : toolsObject.getClass().getDeclaredMethods()) {
            if (!method.isAnnotationPresent(Tool.class)) {
                continue;
            }
            ToolSpecification spec = ToolSpecifications.toolSpecificationFrom(method);
            if (allowed.contains(spec.name())) {
                ToolExecutor tool = new DefaultToolExecutor(toolsObject, method);
                result.add(spec, new GuardedToolExecutor(tool, guard));
            }
        }
        return result.build();
    }

    static class GuardedToolExecutor implements ToolExecutor {

        private final ToolExecutor delegate;
        private final ToolGuard guard;

        GuardedToolExecutor(ToolExecutor delegate, ToolGuard guard) {
            this.delegate = delegate;
            this.guard = guard;
        }

        @Override
        public ToolExecutionResult executeWithContext(ToolExecutionRequest request, InvocationContext context) {
            InvocationParameters params = context.invocationParameters();
            Map<String, Object> args = JSON.readValue(request.arguments(), new TypeReference<Map<String, Object>>() {
            });
            ToolCall call = new ToolCall(params.get("user"), params.get("role"), params.get("customerId"),
                    request.name(), args);

            Decision decision = guard.evaluate(call);
            if (!decision.allowed()) {
                return ToolExecutionResult.builder().resultText(decision.toModelText()).build();
            }
            return delegate.executeWithContext(request, context);
        }

        @Override
        public String execute(ToolExecutionRequest request, Object memoryId) {
            return Decision.deny("context", "no user on this request").toModelText();
        }
    }
}
