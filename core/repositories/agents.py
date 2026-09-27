from typing import Any

from psycopg.types.json import Jsonb

from core.database.connection import get_connection


class AgentRepository:
    """
    Handles persistent agent identity and lifecycle data.
    """

    def create_agent(
        self,
        name: str,
        role: str,
        parent_agent_id: str | None = None,
        model_provider: str | None = None,
        model_name: str | None = None,
        system_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO agents (
                        name,
                        role,
                        parent_agent_id,
                        model_provider,
                        model_name,
                        system_prompt,
                        metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        name,
                        role,
                        parent_agent_id,
                        model_provider,
                        model_name,
                        system_prompt,
                        Jsonb(metadata or {}),
                    ),
                )

                agent_id = cursor.fetchone()[0]

            connection.commit()

        return str(agent_id)

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        role,
                        parent_agent_id,
                        status,
                        model_provider,
                        model_name,
                        system_prompt,
                        metadata,
                        created_at,
                        updated_at
                    FROM agents
                    WHERE id = %s;
                    """,
                    (agent_id,),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [description.name for description in cursor.description]

                return dict(zip(columns, row))

    def update_status(
        self,
        agent_id: str,
        status: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE agents
                    SET
                        status = %s,
                        updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (status, agent_id),
                )

            connection.commit()

    def assign_parent(
        self,
        agent_id: str,
        parent_agent_id: str | None,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE agents
                    SET
                        parent_agent_id = %s,
                        updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (parent_agent_id, agent_id),
                )

            connection.commit()

    def delete_agent(
        self,
        agent_id: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM agents
                    WHERE id = %s;
                    """,
                    (agent_id,),
                )

            connection.commit()