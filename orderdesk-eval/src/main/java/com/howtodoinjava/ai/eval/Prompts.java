package com.howtodoinjava.ai.eval;

public final class Prompts {

    private Prompts() {
    }

    /** Zero-shot: the task and the allowed labels, no examples. */
    public static final String ZERO_SHOT = """
            You triage customer support tickets for an online shop.
            Classify the ticket into one category and one priority.
            Categories: BILLING, SHIPPING, RETURNS, ACCOUNT, PRODUCT.
            Priorities: LOW, NORMAL, HIGH.
            Answer with JSON only: {"category": "...", "priority": "..."}
            """;

    /** Few-shot: the same instructions plus six labelled examples. */
    public static final String FEW_SHOT = ZERO_SHOT + """

            Examples:
            Ticket: My payment failed but the money left my bank account.
            Answer: {"category": "BILLING", "priority": "HIGH"}
            Ticket: Can I get the invoice with my company name on it?
            Answer: {"category": "BILLING", "priority": "LOW"}
            Ticket: My parcel has been stuck at the depot for a week.
            Answer: {"category": "SHIPPING", "priority": "NORMAL"}
            Ticket: The mug arrived broken, I'd like a new one.
            Answer: {"category": "RETURNS", "priority": "NORMAL"}
            Ticket: I think someone else is logged in to my account.
            Answer: {"category": "ACCOUNT", "priority": "HIGH"}
            Ticket: Is the tent suitable for winter camping?
            Answer: {"category": "PRODUCT", "priority": "LOW"}
            """;
}
