package com.howtodoinjava.sandbox;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;

/**
 * The code tool as a Spring AI tool. Register it with ChatClient.prompt().tools(new OrderDeskTools(...)).
 */
public class OrderDeskTools {

    private final OrderDeskCodeTool codeTool;

    public OrderDeskTools(CodeSandbox sandbox, String ordersJson) {
        this.codeTool = new OrderDeskCodeTool(sandbox, ordersJson);
    }

    @Tool(description = "Runs JavaScript over the array 'orders' (id, status, total) and returns the last expression")
    public String runJavaScript(@ToolParam(description = "JavaScript code") String code) {
        return codeTool.runJavaScript(code);
    }
}
