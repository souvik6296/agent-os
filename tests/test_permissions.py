from core.database.connection import get_connection
from core.repositories.permissions import PermissionRepository


def test_permission_grant_and_check():
    repository = PermissionRepository()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agents (name, role)
                VALUES (%s, %s)
                RETURNING id;
                """,
                ("permission-test-worker", "worker"),
            )

            agent_id = str(cursor.fetchone()[0])

        connection.commit()

    permission_id = None

    try:
        permission_id = repository.create_permission(
            name="TEST_WRITE",
            description="Temporary test permission.",
            risk_level="low",
        )

        assert repository.has_permission(
            agent_id,
            "TEST_WRITE",
        ) is False

        repository.grant_permission(
            agent_id=agent_id,
            permission_id=permission_id,
        )

        assert repository.has_permission(
            agent_id,
            "TEST_WRITE",
        ) is True

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM agent_permissions
                    WHERE agent_id = %s;
                    """,
                    (agent_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM permissions
                    WHERE id = %s;
                    """,
                    (permission_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM agents
                    WHERE id = %s;
                    """,
                    (agent_id,),
                )

            connection.commit()