package com.howtodoinjava.guardrails.guard;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import com.cedarpolicy.AuthorizationEngine;
import com.cedarpolicy.BasicAuthorizationEngine;
import com.cedarpolicy.model.AuthorizationRequest;
import com.cedarpolicy.model.AuthorizationResponse;
import com.cedarpolicy.model.AuthorizationSuccessResponse;
import com.cedarpolicy.model.entity.Entity;
import com.cedarpolicy.model.policy.Policy;
import com.cedarpolicy.model.policy.PolicySet;
import com.cedarpolicy.value.EntityTypeName;
import com.cedarpolicy.value.EntityUID;
import com.cedarpolicy.value.PrimBool;
import com.cedarpolicy.value.PrimLong;
import com.cedarpolicy.value.Value;

/**
 * Asks the embedded Cedar engine whether a refund is allowed. If it isn't, but would be
 * with an approval, the call goes to a person. Any error denies the call (fail closed).
 */
public class CedarRefundPolicy implements Gate {

    private static final EntityTypeName USER = EntityTypeName.parse("OrderDesk::User").orElseThrow();
    private static final EntityTypeName ROLE = EntityTypeName.parse("OrderDesk::Role").orElseThrow();
    private static final EntityTypeName ACTION = EntityTypeName.parse("OrderDesk::Action").orElseThrow();
    private static final EntityTypeName ORDER = EntityTypeName.parse("OrderDesk::Order").orElseThrow();

    private final AuthorizationEngine engine = new BasicAuthorizationEngine();
    private final PolicySet policies;
    private final ApprovalService approvals;

    public CedarRefundPolicy(String policyText, ApprovalService approvals) {
        try {
            this.policies = withIdsFromAnnotations(PolicySet.parsePolicies(policyText));
        } catch (Exception e) {
            throw new IllegalStateException("Invalid Cedar policies", e);
        }
        this.approvals = approvals;
    }

    /** Cedar Java names parsed policies policy0, policy1, ...; we use their @id annotations instead. */
    private static PolicySet withIdsFromAnnotations(PolicySet parsed) throws Exception {
        Set<Policy> named = new HashSet<>();
        for (Map.Entry<String, String> entry : parsed.getStaticPolicies().entrySet()) {
            String id = new Policy(entry.getValue(), entry.getKey()).getAnnotation("id");
            named.add(new Policy(entry.getValue(), id != null ? id : entry.getKey()));
        }
        return new PolicySet(named);
    }

    public static CedarRefundPolicy fromClasspath(String resource, ApprovalService approvals) {
        try (InputStream in = CedarRefundPolicy.class.getClassLoader().getResourceAsStream(resource)) {
            return new CedarRefundPolicy(new String(in.readAllBytes(), StandardCharsets.UTF_8), approvals);
        } catch (IOException | NullPointerException e) {
            throw new IllegalStateException("Cannot read " + resource, e);
        }
    }

    @Override
    public Decision check(ToolCall call) {
        if (!call.tool().equals("issueRefund")) {
            return Decision.allow();
        }
        try {
            boolean approved = approvals.isApproved(call);
            AuthorizationSuccessResponse result = authorize(call, approved);
            if (result.isAllowed()) {
                return Decision.allow();
            }
            if (!approved && authorize(call, true).isAllowed()) {
                ApprovalService.Approval approval = approvals.request(call);
                return Decision.pending("approval", "refunds above 100 USD need a supervisor's approval",
                        approval.id());
            }
            return Decision.deny("policy", "Cedar denied the refund (policies: " + result.getReason() + ")");
        } catch (Exception e) {
            return Decision.deny("policy", "policy check failed, denying by default");
        }
    }

    @Override
    public void onAllowed(ToolCall call) {
        approvals.consume(call);
    }

    AuthorizationSuccessResponse authorize(ToolCall call, boolean approved) throws Exception {
        EntityUID role = ROLE.of(call.role());
        Entity user = new Entity(USER.of(call.user()), Map.of(), Set.of(role));
        long amountCents = call.decimal("amount").movePointRight(2).longValueExact();
        Map<String, Value> context = Map.of(
                "amountCents", new PrimLong(amountCents),
                "approved", new PrimBool(approved));

        AuthorizationRequest request = new AuthorizationRequest(
                user.getEUID(), ACTION.of("issueRefund"), ORDER.of(call.text("orderId")), context);
        AuthorizationResponse response = engine.isAuthorized(request, policies, Set.of(user));
        return response.success.orElseThrow(() -> new IllegalStateException("Cedar error: " + response));
    }
}
