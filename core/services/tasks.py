from typing import Any

from core.repositories.task_reviews import TaskReviewRepository
from core.repositories.tasks import TaskRepository


class TaskService:
    """
    Business logic for task creation and lifecycle management.

    Persistence is handled by TaskRepository and TaskReviewRepository.
    Governance and agent authorization will be integrated here
    as the task system becomes autonomous.
    """

    VALID_STATUSES = {
        "created",
        "planned",
        "assigned",
        "running",
        "waiting",
        "review",
        "completed",
        "failed",
        "cancelled",
    }

    VALID_PRIORITIES = {
        "low",
        "normal",
        "high",
        "critical",
    }

    TRANSITIONS = {
        "created": {
            "planned",
            "cancelled",
        },
        "planned": {
            "assigned",
            "cancelled",
        },
        "assigned": {
            "running",
            "cancelled",
        },
        "running": {
            "waiting",
            "review",
            "completed",
            "failed",
            "cancelled",
        },
        "waiting": {
            "running",
            "cancelled",
        },
        "review": {
            "running",
            "completed",
            "failed",
            "cancelled",
        },
        "completed": set(),
        "failed": set(),
        "cancelled": set(),
    }

    def __init__(
        self,
        repository: TaskRepository | None = None,
        review_repository: TaskReviewRepository | None = None,
    ):
        self.repository = repository or TaskRepository()
        self.review_repository = review_repository or TaskReviewRepository()

    def create_task(
        self,
        title: str,
        description: str | None = None,
        project_id: str | None = None,
        parent_task_id: str | None = None,
        assigned_agent_id: str | None = None,
        assigned_team_id: str | None = None,
        priority: str = "normal",
        input_data: dict[str, Any] | None = None,
        output_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        requires_review: bool = False,
    ) -> str:
        """
        Create a new task in the CREATED state.
        """

        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        title = title.strip()

        if priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"Invalid task priority: {priority}"
            )

        return self.repository.create_task(
            title=title,
            description=description,
            project_id=project_id,
            parent_task_id=parent_task_id,
            assigned_agent_id=assigned_agent_id,
            assigned_team_id=assigned_team_id,
            status="created",
            priority=priority,
            input_data=input_data,
            output_data=output_data,
            metadata=metadata,
            requires_review=requires_review,
        )

    def transition_task(
        self,
        task_id: str,
        new_status: str,
    ) -> None:
        """
        Move a task through the allowed lifecycle.

        Only valid state transitions are accepted.
        """

        if new_status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid task status: {new_status}"
            )

        task = self.repository.get_task(task_id)

        if task is None:
            raise ValueError(
                f"Task not found: {task_id}"
            )

        current_status = task["status"]

        allowed_transitions = self.TRANSITIONS.get(
            current_status,
            set(),
        )

        if new_status not in allowed_transitions:
            raise ValueError(
                "Invalid task transition: "
                f"{current_status} -> {new_status}"
            )

        # A task requiring review must enter REVIEW before completion.
        if (
            current_status == "running"
            and new_status == "completed"
            and task["requires_review"]
        ):
            raise ValueError(
                "Task requires review before completion"
            )

        if (
            current_status == "review"
            and new_status == "completed"
            and task["requires_review"]
        ):
            latest_review = self.review_repository.get_latest_review(task_id)
            if latest_review is None:
                raise ValueError(
                    "Task requires a review before completion"
                )
            if latest_review["result"] != "pass":
                raise ValueError(
                    "Task cannot be completed because latest review did not pass"
                )

        self.repository.update_status(
            task_id=task_id,
            status=new_status,
        )

    def record_review(
        self,
        task_id: str,
        reviewer_agent_id: str,
        result: str,
        test_cases: list[Any] | None = None,
        test_results: dict[str, Any] | None = None,
        findings: list[Any] | None = None,
        report: str | None = None,
        attempt_number: int | None = None,
    ) -> str:
        """
        Record a review attempt for a task.

        If the task requires review, it must be in the 'review' status.
        If the review result is 'fail', the task returns to 'running'.
        """
        task = self.repository.get_task(task_id)
        if task is None:
            raise ValueError(f"Task not found: {task_id}")

        if task["status"] != "review":
            raise ValueError(
                f"Cannot record review for task in status: {task['status']}. Task must be in 'review' status."
            )

        if result not in {"pass", "fail"}:
            raise ValueError(
                f"Invalid review result: {result}. Must be 'pass' or 'fail'."
            )

        if attempt_number is None:
            latest = self.review_repository.get_latest_review(task_id)
            attempt_number = (latest["attempt_number"] + 1) if latest else 1

        review_id = self.review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_agent_id,
            attempt_number=attempt_number,
            result=result,
            test_cases=test_cases,
            test_results=test_results,
            findings=findings,
            report=report,
        )

        if result == "fail":
            self.repository.update_status(
                task_id=task_id,
                status="running",
            )

        return review_id

    def get_reviews(self, task_id: str) -> list[dict[str, Any]]:
        return self.review_repository.list_reviews(task_id)

    def get_latest_review(self, task_id: str) -> dict[str, Any] | None:
        return self.review_repository.get_latest_review(task_id)
