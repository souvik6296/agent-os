from core.database.connection import get_connection
from core.services.governance import GovernanceService


def test_governance_service_allows_normal_action():
    service = GovernanceService()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agents (name, role)
                VALUES (%s, %s)
                RETURNING id;
                """,
                ("service-test-worker", "worker"),
            )

            agent_id = str(cursor.fetchone()[0])

        connection.commit()

    try:
        result = service.authorize(
            agent_id=agent_id,
            role="worker",
            action="create_file",
            resource="workspace/test.txt",
        )

        assert result["decision"] == "ALLOW"
        assert result["request_id"]
        assert result["decision_id"]
        assert result["audit_id"]

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM audit_logs
                    WHERE agent_id = %s;
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_decisions
                    WHERE request_id IN (
                        SELECT id
                        FROM governance_requests
                        WHERE agent_id = %s
                    );
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_requests
                    WHERE agent_id = %s;
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM agents
                    WHERE id = %s;
                    """,
                    (agent_id,),
                )

            connection.commit()


def test_governance_service_denies_constitution_modification():
    service = GovernanceService()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agents (name, role)
                VALUES (%s, %s)
                RETURNING id;
                """,
                ("service-test-worker", "worker"),
            )

            agent_id = str(cursor.fetchone()[0])

        connection.commit()

    try:
        result = service.authorize(
            agent_id=agent_id,
            role="worker",
            action="modify",
            resource="constitution",
        )

        assert result["decision"] == "DENY"
        assert result["policy"] == "core_protection"

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM audit_logs
                    WHERE agent_id = %s;
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_decisions
                    WHERE request_id IN (
                        SELECT id
                        FROM governance_requests
                        WHERE agent_id = %s
                    );
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_requests
                    WHERE agent_id = %s;
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM agents
                    WHERE id = %s;
                    """,
                    (agent_id,),
                )

            connection.commit()