// Amounts are in cents: Cedar compares whole numbers (Long).

// A support agent may refund up to 100 USD on their own.
@id("support-small-refund")
permit (
    principal in OrderDesk::Role::"support",
    action == OrderDesk::Action::"issueRefund",
    resource
)
when { context.amountCents <= 10000 };

// Up to 1,000 USD when a supervisor approved this exact call.
@id("support-approved-refund")
permit (
    principal in OrderDesk::Role::"support",
    action == OrderDesk::Action::"issueRefund",
    resource
)
when { context.amountCents <= 100000 && context.approved };

// A supervisor may refund up to 1,000 USD.
@id("supervisor-refund")
permit (
    principal in OrderDesk::Role::"supervisor",
    action == OrderDesk::Action::"issueRefund",
    resource
)
when { context.amountCents <= 100000 };

// Nothing above 1,000 USD goes through the agent, whoever asks.
@id("agent-refund-cap")
forbid (
    principal,
    action == OrderDesk::Action::"issueRefund",
    resource
)
when { context.amountCents > 100000 };
