from typing import Any

from psycopg.types.json import Jsonb

from core.database.connection import get_connection


class GovernanceRepository:
    """
    Handles persistent governance data.
    Business rules stay in the Governance Engine.
    """

    def create_request(
        self,
        agent_id: str,
        task_id: str | None,
        action: str,
        resource: str,
        requested_permissions: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> str:

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO governance_requests (
                        agent_id,
                        task_id,
                        action,
                        resource,
                        requested_permissions,
                        context
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        agent_id,
                        task_id,
                        action,
                        resource,
                        Jsonb(requested_permissions or []),
			Jsonb(context or {}),
                    ),
                )

                request_id = cursor.fetchone()[0]

            connection.commit()

        return str(request_id)

    def save_decision(
        self,
        request_id: str,
        decision: str,
        policy_id: str,
        reason: str,
        evaluator: str = "deterministic",
        evaluation_data: dict[str, Any] | None = None,
    ) -> str:

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO governance_decisions (
                        request_id,
                        decision,
                        policy_id,
                        reason,
                        evaluator,
                        evaluation_data
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        request_id,
                        decision,
                        policy_id,
                        reason,
                        evaluator,
                        Jsonb(evaluation_data or {}),
                    ),
                )

                decision_id = cursor.fetchone()[0]

                new_status = {
                    "ALLOW": "approved",
                    "DENY": "denied",
                }.get(decision, "pending")

                cursor.execute(
                    """
                    UPDATE governance_requests
                    SET status = %s
                    WHERE id = %s;
                    """,
                    (new_status, request_id),
                )

            connection.commit()

        return str(decision_id)

    def create_audit_log(
        self,
        agent_id: str,
        task_id: str | None,
        governance_request_id: str,
        action: str,
        resource: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> str:

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO audit_logs (
                        agent_id,
                        task_id,
                        governance_request_id,
                        action,
                        resource,
                        result,
                        details
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        agent_id,
                        task_id,
                        governance_request_id,
                        action,
                        resource,
                        result,
                        Jsonb(details or {}),
                    ),
                )

                audit_id = cursor.fetchone()[0]

            connection.commit()

        return str(audit_id)