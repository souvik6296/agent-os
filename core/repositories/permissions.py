from typing import Any

from psycopg.types.json import Jsonb

from core.database.connection import get_connection


class PermissionRepository:
    """
    Handles persistent agent permissions.
    """

    def create_permission(
        self,
        name: str,
        description: str,
        risk_level: str = "low",
    ) -> str:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO permissions (
                        name,
                        description,
                        risk_level
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name)
                    DO UPDATE SET
                        description = EXCLUDED.description,
                        risk_level = EXCLUDED.risk_level
                    RETURNING id;
                    """,
                    (
                        name,
                        description,
                        risk_level,
                    ),
                )

                permission_id = cursor.fetchone()[0]

            connection.commit()

        return str(permission_id)

    def grant_permission(
        self,
        agent_id: str,
        permission_id: str,
        granted_by_agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO agent_permissions (
                        agent_id,
                        permission_id,
                        granted_by_agent_id,
                        metadata
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (agent_id, permission_id)
                    DO UPDATE SET
                        granted_by_agent_id = EXCLUDED.granted_by_agent_id,
                        metadata = EXCLUDED.metadata;
                    """,
                    (
                        agent_id,
                        permission_id,
                        granted_by_agent_id,
                        Jsonb(metadata or {}),
                    ),
                )

            connection.commit()

    def has_permission(
        self,
        agent_id: str,
        permission_name: str,
    ) -> bool:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM agent_permissions ap
                        JOIN permissions p
                            ON p.id = ap.permission_id
                        WHERE ap.agent_id = %s
                          AND p.name = %s
                          AND (
                              ap.expires_at IS NULL
                              OR ap.expires_at > NOW()
                          )
                    );
                    """,
                    (
                        agent_id,
                        permission_name,
                    ),
                )

                return cursor.fetchone()[0]