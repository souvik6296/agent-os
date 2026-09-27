from typing import Any

from core.governance.engine import GovernanceEngine, GovernanceRequest
from core.repositories.governance import GovernanceRepository


class GovernanceService:
    """
    Coordinates governance evaluation and persistence.

    Flow:
        Request
          ↓
        Governance Engine
          ↓
        Repository
          ↓
        PostgreSQL
    """

    def __init__(
        self,
        engine: GovernanceEngine | None = None,
        repository: GovernanceRepository | None = None,
    ):
        self.engine = engine or GovernanceEngine()
        self.repository = repository or GovernanceRepository()

    def authorize(
        self,
        agent_id: str,
        role: str,
        action: str,
        resource: str,
        task_id: str | None = None,
        requested_permissions: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ):
        request_context = context or {}

        # 1. Persist the governance request.
        request_id = self.repository.create_request(
            agent_id=agent_id,
            task_id=task_id,
            action=action,
            resource=resource,
            requested_permissions=requested_permissions,
            context=request_context,
        )

        # 2. Build the request for the deterministic engine.
        governance_request = GovernanceRequest(
            agent_id=agent_id,
            role=role,
            action=action,
            resource=resource,
            context=request_context,
        )

        # 3. Evaluate constitutional rules.
        decision = self.engine.evaluate(governance_request)

        # 4. Persist the decision.
        decision_id = self.repository.save_decision(
            request_id=request_id,
            decision=decision.decision,
            policy_id=decision.policy,
            reason=decision.reason,
        )

        # 5. Always create an audit record.
        audit_id = self.repository.create_audit_log(
            agent_id=agent_id,
            task_id=task_id,
            governance_request_id=request_id,
            action=action,
            resource=resource,
            result=decision.decision,
            details={
                "policy": decision.policy,
                "reason": decision.reason,
            },
        )

        return {
            "request_id": request_id,
            "decision_id": decision_id,
            "audit_id": audit_id,
            "decision": decision.decision,
            "reason": decision.reason,
            "policy": decision.policy,
        }