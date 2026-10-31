package com.howtodoinjava.sandbox;

/**
 * The agent's "code tool": runs a JavaScript snippet over the order data and returns the result.
 * The orders are passed in as plain JSON data, never as Java objects.
 */
public class OrderDeskCodeTool {

    private final CodeSandbox sandbox;
    private final String ordersJson;

    public OrderDeskCodeTool(CodeSandbox sandbox, String ordersJson) {
        this.sandbox = sandbox;
        this.ordersJson = ordersJson;
    }

    public String runJavaScript(String code) {
        String program = "globalThis.orders = " + ordersJson + ";\n" + code;
        ExecutionResult result = sandbox.run(program);
        return result.succeeded()
                ? result.output()
                : "Code failed (" + result.status() + "): " + result.output();
    }
}
