from core.repositories.governance import GovernanceRepository
from core.database.connection import get_connection


def test_governance_repository_flow():
    repository = GovernanceRepository()

    # Create a temporary test agent.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agents (name, role)
                VALUES (%s, %s)
                RETURNING id;
                """,
                ("test-worker", "worker"),
            )

            agent_id = str(cursor.fetchone()[0])

        connection.commit()

    try:
        request_id = repository.create_request(
            agent_id=agent_id,
            task_id=None,
            action="create_file",
            resource="test_workspace",
            requested_permissions=["WRITE"],
            context={
                "test": True,
            },
        )

        decision_id = repository.save_decision(
            request_id=request_id,
            decision="ALLOW",
            policy_id="autonomous_action",
            reason="Test governance decision.",
        )

        audit_id = repository.create_audit_log(
            agent_id=agent_id,
            task_id=None,
            governance_request_id=request_id,
            action="create_file",
            resource="test_workspace",
            result="ALLOWED",
            details={
                "test": True,
            },
        )

        assert request_id
        assert decision_id
        assert audit_id

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT status
                    FROM governance_requests
                    WHERE id = %s;
                    """,
                    (request_id,),
                )

                status = cursor.fetchone()[0]

        assert status == "approved"

    finally:
        # Remove test data in dependency order.
        with get_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM audit_logs
                    WHERE governance_request_id = %s;
                    """,
                    (request_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_decisions
                    WHERE request_id = %s;
                    """,
                    (request_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_requests
                    WHERE id = %s;
                    """,
                    (request_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM agents
                    WHERE id = %s;
                    """,
                    (agent_id,),
                )

            connection.commit()