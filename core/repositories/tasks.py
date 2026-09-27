from typing import Any

from psycopg.types.json import Jsonb

from core.database.connection import get_connection


class TaskRepository:
    """
    Handles database operations for tasks.

    This repository contains persistence logic only.
    Business rules and governance belong in the service layer.
    """

    def create_task(
        self,
        title: str,
        description: str | None = None,
        project_id: str | None = None,
        parent_task_id: str | None = None,
        assigned_agent_id: str | None = None,
        assigned_team_id: str | None = None,
        status: str = "created",
        priority: str = "normal",
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        requires_review: bool = False,
    ) -> str:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (
                        project_id,
                        parent_task_id,
                        assigned_agent_id,
                        assigned_team_id,
                        title,
                        description,
                        status,
                        priority,
                        input_data,
                        output_data,
                        metadata,
                        requires_review
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING id;
                    """,
                    (
                        project_id,
                        parent_task_id,
                        assigned_agent_id,
                        assigned_team_id,
                        title,
                        description,
                        status,
                        priority,
                        Jsonb(input_data or {}),
                        Jsonb(output_data or {}),
                        Jsonb(metadata or {}),
                        requires_review,
                    ),
                )

                task_id = cursor.fetchone()[0]

            connection.commit()

        return str(task_id)

    def get_task(
        self,
        task_id: str,
    ) -> dict[str, Any] | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        project_id,
                        parent_task_id,
                        assigned_agent_id,
                        assigned_team_id,
                        title,
                        description,
                        status,
                        priority,
                        input_data,
                        output_data,
                        metadata,
                        requires_review,
                        created_at,
                        started_at,
                        completed_at,
                        updated_at
                    FROM tasks
                    WHERE id = %s;
                    """,
                    (task_id,),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def list_tasks(
        self,
        status: str | None = None,
        assigned_agent_id: str | None = None,
        assigned_team_id: str | None = None,
        parent_task_id: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                id,
                project_id,
                parent_task_id,
                assigned_agent_id,
                assigned_team_id,
                title,
                description,
                status,
                priority,
                input_data,
                output_data,
                metadata,
                requires_review,
                created_at,
                started_at,
                completed_at,
                updated_at
            FROM tasks
            WHERE 1 = 1
        """

        parameters: list[Any] = []

        if status is not None:
            query += " AND status = %s"
            parameters.append(status)

        if assigned_agent_id is not None:
            query += " AND assigned_agent_id = %s"
            parameters.append(assigned_agent_id)

        if assigned_team_id is not None:
            query += " AND assigned_team_id = %s"
            parameters.append(assigned_team_id)

        if parent_task_id is not None:
            query += " AND parent_task_id = %s"
            parameters.append(parent_task_id)

        query += " ORDER BY created_at ASC;"

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)

                rows = cursor.fetchall()

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    def update_status(
        self,
        task_id: str,
        status: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        status = %s,
                        started_at = CASE
                            WHEN %s = 'running'
                                AND started_at IS NULL
                            THEN NOW()
                            ELSE started_at
                        END,
                        completed_at = CASE
                            WHEN %s IN (
                                'completed',
                                'failed',
                                'cancelled'
                            )
                            THEN NOW()
                            ELSE completed_at
                        END,
                        updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (
                        status,
                        status,
                        status,
                        task_id,
                    ),
                )

            connection.commit()

    def assign_agent(
        self,
        task_id: str,
        agent_id: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        assigned_agent_id = %s,
                        assigned_team_id = NULL,
                        updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (
                        agent_id,
                        task_id,
                    ),
                )

            connection.commit()

    def assign_team(
        self,
        task_id: str,
        team_id: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        assigned_team_id = %s,
                        assigned_agent_id = NULL,
                        updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (
                        team_id,
                        task_id,
                    ),
                )

            connection.commit()

    def update_output(
        self,
        task_id: str,
        output_data: dict[str, Any],
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tasks
                    SET
                        output_data = %s,
                        updated_at = NOW()
                    WHERE id = %s;
                    """,
                    (
                        Jsonb(output_data),
                        task_id,
                    ),
                )

            connection.commit()

    def delete_task(
        self,
        task_id: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM tasks
                    WHERE id = %s;
                    """,
                    (task_id,),
                )

            connection.commit()
