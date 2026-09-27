from dataclasses import dataclass
from typing import Any


@dataclass
class GovernanceRequest:
    agent_id: str
    role: str
    action: str
    resource: str
    context: dict[str, Any]


@dataclass
class GovernanceDecision:
    decision: str
    reason: str
    policy: str


class GovernanceEngine:
    """
    Initial deterministic Governance Engine.

    The engine evaluates hard constitutional rules before
    an agent is allowed to perform a governed action.
    """

    PROTECTED_RESOURCES = {
        "constitution",
        "governance_engine",
        "root_identity",
        "root_permissions",
        "audit_system",
    }

    def evaluate(self, request: GovernanceRequest) -> GovernanceDecision:

        # Article 5 — Constitutional Protection
        if request.resource in self.PROTECTED_RESOURCES:
            if request.role != "owner":
                return GovernanceDecision(
                    decision="DENY",
                    reason="Protected core resource.",
                    policy="core_protection",
                )

        # Permission Enforcement
        if not request.context.get("permissions_satisfied", True):
            missing_permissions = request.context.get(
                "missing_permissions",
                [],
            )

            return GovernanceDecision(
                decision="DENY",
                reason=(
                    "Required permission(s) missing: "
                    + ", ".join(missing_permissions)
                ),
                policy="permission_required",
            )

        # Article 2 — Hierarchy Authority
        if request.context.get("exceeds_role_authority", False):
            return GovernanceDecision(
                decision="DENY",
                reason="Agent exceeds its assigned authority.",
                policy="hierarchy_authority",
            )

        # Article 6 — Least Authority
        if request.context.get("exceeds_required_scope", False):
            return GovernanceDecision(
                decision="DENY",
                reason="Requested permission exceeds required scope.",
                policy="least_authority",
            )

        # Article 12 — Resource Governance
        if request.context.get("resource_limit_exceeded", False):
            return GovernanceDecision(
                decision="DENY",
                reason="Configured resource limit exceeded.",
                policy="resource_limits",
            )

        # Article 13 — Security
        if request.context.get("security_violation", False):
            return GovernanceDecision(
                decision="DENY",
                reason="Security policy violation.",
                policy="security_protection",
            )

        # Article 7 — Auditability
        if request.context.get("requires_audit", False):
            if not request.context.get("audit_available", False):
                return GovernanceDecision(
                    decision="DENY",
                    reason="Required audit mechanism is unavailable.",
                    policy="audit_required",
                )

        # Article 14 — Reversibility
        if request.context.get("rollback_required", False):
            if not request.context.get("rollback_available", False):
                return GovernanceDecision(
                    decision="DENY",
                    reason="Required rollback mechanism is unavailable.",
                    policy="reversibility",
                )

        # If all mandatory rules pass, autonomous execution is allowed.
        return GovernanceDecision(
            decision="ALLOW",
            reason="All deterministic governance checks passed.",
            policy="autonomous_action",
        )