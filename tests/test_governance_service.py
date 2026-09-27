from core.database.connection import get_connection
from core.services.governance import GovernanceService
from core.repositories.permissions import PermissionRepository


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

def test_governance_service_denies_missing_permission():
    service = GovernanceService()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agents (name, role)
                VALUES (%s, %s)
                RETURNING id;
                """,
                ("permission-test-worker-denied", "worker"),
            )
            agent_id = str(cursor.fetchone()[0])
        connection.commit()

    try:
        result = service.authorize(
            agent_id=agent_id,
            role="worker",
            action="create_file",
            resource="workspace/test.txt",
            requested_permissions=["FILE_WRITE"],
        )

        assert result["decision"] == "DENY"
        assert result["policy"] == "permission_required"
        assert "FILE_WRITE" in result["missing_permissions"]
        assert result["request_id"]
        assert result["decision_id"]
        assert result["audit_id"]

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM audit_logs WHERE agent_id = %s;",
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
                    "DELETE FROM agents WHERE id = %s;",
                    (agent_id,),
                )
            connection.commit()


def test_governance_service_allows_granted_permission():
    service = GovernanceService()

    permission_repository = PermissionRepository()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agents (name, role)
                VALUES (%s, %s)
                RETURNING id;
                """,
                ("permission-test-worker-allowed", "worker"),
            )
            agent_id = str(cursor.fetchone()[0])
        connection.commit()

    permission_id = permission_repository.create_permission(
        name="FILE_WRITE",
        description="Allows an agent to create and modify files.",
        risk_level="low",
    )

    permission_repository.grant_permission(
        agent_id=agent_id,
        permission_id=permission_id,
    )

    try:
        result = service.authorize(
            agent_id=agent_id,
            role="worker",
            action="create_file",
            resource="workspace/test.txt",
            requested_permissions=["FILE_WRITE"],
        )

        assert result["decision"] == "ALLOW"
        assert result["missing_permissions"] == []
        assert result["request_id"]
        assert result["decision_id"]
        assert result["audit_id"]

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM audit_logs WHERE agent_id = %s;",
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
                    "DELETE FROM agent_permissions WHERE agent_id = %s;",
                    (agent_id,),
                )
                cursor.execute(
                    "DELETE FROM agents WHERE id = %s;",
                    (agent_id,),
                )
                cursor.execute(
                    "DELETE FROM permissions WHERE id = %s;",
                    (permission_id,),
                )
            connection.commit()