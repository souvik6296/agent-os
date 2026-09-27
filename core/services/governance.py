from typing import Any

from core.governance.engine import GovernanceEngine, GovernanceRequest
from core.repositories.governance import GovernanceRepository
from core.repositories.permissions import PermissionRepository


class GovernanceService:
    """
    Coordinates permission checks, governance evaluation, and persistence.

    Flow:

        Agent
          ↓
        Permission Check
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
        permission_repository: PermissionRepository | None = None,
    ):
        self.engine = engine or GovernanceEngine()
        self.repository = repository or GovernanceRepository()
        self.permission_repository = (
            permission_repository or PermissionRepository()
        )

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
        request_context = dict(context or {})

        required_permissions = requested_permissions or []

        # 1. Check permissions against the persistent permission registry.
        missing_permissions = [
            permission
            for permission in required_permissions
            if not self.permission_repository.has_permission(
                agent_id,
                permission,
            )
        ]

        permissions_satisfied = len(missing_permissions) == 0

        # Pass permission state into the deterministic governance engine.
        request_context["required_permissions"] = required_permissions
        request_context["missing_permissions"] = missing_permissions
        request_context["permissions_satisfied"] = permissions_satisfied

        # 2. Persist the governance request.
        request_id = self.repository.create_request(
            agent_id=agent_id,
            task_id=task_id,
            action=action,
            resource=resource,
            requested_permissions=required_permissions,
            context=request_context,
        )

        # 3. Build the request for the deterministic engine.
        governance_request = GovernanceRequest(
            agent_id=agent_id,
            role=role,
            action=action,
            resource=resource,
            context=request_context,
        )

        # 4. Evaluate constitutional and governance rules.
        decision = self.engine.evaluate(governance_request)

        # 5. Persist the governance decision.
        decision_id = self.repository.save_decision(
            request_id=request_id,
            decision=decision.decision,
            policy_id=decision.policy,
            reason=decision.reason,
        )

        # 6. Persist an audit record.
        audit_id = self.repository.create_audit_log(
            agent_id=agent_id,
            task_id=task_id,
            governance_request_id=request_id,
            action=action,
            resource=resource,
            result=decision.decision,
            details={
                "reason": decision.reason,
                "policy": decision.policy,
                "required_permissions": required_permissions,
                "missing_permissions": missing_permissions,
            },
        )

        return {
            "request_id": request_id,
            "decision_id": decision_id,
            "audit_id": audit_id,
            "decision": decision.decision,
            "reason": decision.reason,
            "policy": decision.policy,
            "missing_permissions": missing_permissions,
        }