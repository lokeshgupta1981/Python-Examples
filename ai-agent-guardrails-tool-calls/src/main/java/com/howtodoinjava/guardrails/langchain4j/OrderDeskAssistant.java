package com.howtodoinjava.guardrails.langchain4j;

import dev.langchain4j.invocation.InvocationParameters;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.service.UserMessage;

public interface OrderDeskAssistant {

    @SystemMessage("""
            You are OrderDesk, an assistant for support agents handling refunds.
            Use the tools to look up orders and issue refunds.
            Never refund more than 100 USD. Never delete customers.
            Answer in one or two short sentences.""")
    String chat(@UserMessage String message, InvocationParameters session);
}
