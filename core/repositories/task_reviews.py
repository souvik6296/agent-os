from typing import Any

from psycopg.types.json import Jsonb

from core.database.connection import get_connection


class TaskReviewRepository:
    """
    Handles persistence for task review attempts.

    Review decisions and business rules belong in the service layer.
    This repository only stores and retrieves review records.
    """

    def create_review(
        self,
        task_id: str,
        reviewer_agent_id: str,
        attempt_number: int,
        result: str,
        test_cases: list[Any] | None = None,
        test_results: dict[str, Any] | None = None,
        findings: list[Any] | None = None,
        report: str | None = None,
    ) -> str:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO task_reviews (
                        task_id,
                        reviewer_agent_id,
                        attempt_number,
                        result,
                        test_cases,
                        test_results,
                        findings,
                        report,
                        completed_at
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
                        NOW()
                    )
                    RETURNING id;
                    """,
                    (
                        task_id,
                        reviewer_agent_id,
                        attempt_number,
                        result,
                        Jsonb(test_cases or []),
                        Jsonb(test_results or {}),
                        Jsonb(findings or []),
                        report,
                    ),
                )

                review_id = cursor.fetchone()[0]

            connection.commit()

        return str(review_id)

    def get_review(
        self,
        review_id: str,
    ) -> dict[str, Any] | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        task_id,
                        reviewer_agent_id,
                        attempt_number,
                        result,
                        test_cases,
                        test_results,
                        findings,
                        report,
                        created_at,
                        completed_at
                    FROM task_reviews
                    WHERE id = %s;
                    """,
                    (review_id,),
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return dict(zip(columns, row))

    def list_reviews(
        self,
        task_id: str,
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        task_id,
                        reviewer_agent_id,
                        attempt_number,
                        result,
                        test_cases,
                        test_results,
                        findings,
                        report,
                        created_at,
                        completed_at
                    FROM task_reviews
                    WHERE task_id = %s
                    ORDER BY attempt_number ASC;
                    """,
                    (task_id,),
                )

                rows = cursor.fetchall()

                columns = [
                    description.name
                    for description in cursor.description
                ]

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    def get_latest_review(
        self,
        task_id: str,
    ) -> dict[str, Any] | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        task_id,
                        reviewer_agent_id,
                        attempt_number,
                        result,
                        test_cases,
                        test_results,
                        findings,
                        report,
                        created_at,
                        completed_at
                    FROM task_reviews
                    WHERE task_id = %s
                    ORDER BY attempt_number DESC
                    LIMIT 1;
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

    def delete_review(
        self,
        review_id: str,
    ) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM task_reviews
                    WHERE id = %s;
                    """,
                    (review_id,),
                )

            connection.commit()
