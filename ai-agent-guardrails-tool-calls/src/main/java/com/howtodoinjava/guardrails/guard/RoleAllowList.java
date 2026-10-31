package com.howtodoinjava.guardrails.guard;

import java.util.Map;
import java.util.Set;

/**
 * Which tools each role may use. Used twice: to build the tool list for a request,
 * and as the first gate in case the model names a tool anyway.
 */
public class RoleAllowList implements Gate {

    private final Map<String, Set<String>> toolsByRole;

    public RoleAllowList(Map<String, Set<String>> toolsByRole) {
        this.toolsByRole = Map.copyOf(toolsByRole);
    }

    public Set<String> toolsFor(String role) {
        return toolsByRole.getOrDefault(role, Set.of());
    }

    @Override
    public Decision check(ToolCall call) {
        if (toolsFor(call.role()).contains(call.tool())) {
            return Decision.allow();
        }
        return Decision.deny("allow-list", "tool " + call.tool() + " is not available to role " + call.role());
    }
}
