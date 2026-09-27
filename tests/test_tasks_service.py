import pytest

from core.repositories.agents import AgentRepository
from core.repositories.tasks import TaskRepository
from core.services.tasks import TaskService


def test_task_service_creates_task():
    service = TaskService()

    task_id = service.create_task(
        title="Service test task",
        description="Testing task service.",
        priority="high",
    )

    try:
        task = service.repository.get_task(task_id)

        assert task is not None
        assert str(task["id"]) == task_id
        assert task["title"] == "Service test task"
        assert task["status"] == "created"
        assert task["priority"] == "high"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_rejects_empty_title():
    service = TaskService()

    with pytest.raises(
        ValueError,
        match="Task title cannot be empty",
    ):
        service.create_task(
            title="   ",
        )


def test_task_service_moves_created_to_planned():
    service = TaskService()

    task_id = service.create_task(
        title="Planning test task",
    )

    try:
        service.transition_task(
            task_id=task_id,
            new_status="planned",
        )

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "planned"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_moves_planned_to_assigned():
    service = TaskService()

    task_id = service.create_task(
        title="Assignment state test",
    )

    try:
        service.transition_task(
            task_id=task_id,
            new_status="planned",
        )

        service.transition_task(
            task_id=task_id,
            new_status="assigned",
        )

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "assigned"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_moves_assigned_to_running():
    service = TaskService()

    task_id = service.create_task(
        title="Running state test",
    )

    try:
        service.transition_task(
            task_id=task_id,
            new_status="planned",
        )

        service.transition_task(
            task_id=task_id,
            new_status="assigned",
        )

        service.transition_task(
            task_id=task_id,
            new_status="running",
        )

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "running"
        assert task["started_at"] is not None

    finally:
        service.repository.delete_task(task_id)


def test_task_service_allows_running_to_completed():
    service = TaskService()

    task_id = service.create_task(
        title="Simple completion test",
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "completed")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "completed"
        assert task["completed_at"] is not None

    finally:
        service.repository.delete_task(task_id)


def test_task_service_allows_running_to_review():
    service = TaskService()

    task_id = service.create_task(
        title="Review required task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "review"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_rejects_invalid_transition():
    service = TaskService()

    task_id = service.create_task(
        title="Invalid transition test",
    )

    try:
        with pytest.raises(
            ValueError,
            match="Invalid task transition",
        ):
            service.transition_task(
                task_id=task_id,
                new_status="completed",
            )

    finally:
        service.repository.delete_task(task_id)


def test_task_service_allows_waiting_to_running():
    service = TaskService()

    task_id = service.create_task(
        title="Waiting task",
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "waiting")
        service.transition_task(task_id, "running")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "running"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_allows_review_failure_back_to_running():
    service = TaskService()

    task_id = service.create_task(
        title="Review failure task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")
        service.transition_task(task_id, "running")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "running"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_allows_running_to_failed():
    service = TaskService()

    task_id = service.create_task(
        title="Failure test task",
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "failed")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "failed"

    finally:
        service.repository.delete_task(task_id)


def test_task_service_allows_active_task_to_cancelled():
    service = TaskService()

    task_id = service.create_task(
        title="Cancellation test task",
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "cancelled")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "cancelled"

    finally:
        service.repository.delete_task(task_id)


def test_review_required_task_cannot_directly_complete():
    service = TaskService()

    task_id = service.create_task(
        title="Direct complete blocked task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")

        with pytest.raises(
            ValueError,
            match="Task requires review before completion",
        ):
            service.transition_task(task_id, "completed")

    finally:
        service.repository.delete_task(task_id)


def test_review_required_task_enters_review():
    service = TaskService()

    task_id = service.create_task(
        title="Enter review task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "review"

    finally:
        service.repository.delete_task(task_id)


def test_failed_review_returns_task_to_running():
    service = TaskService()
    agent_repository = AgentRepository()

    reviewer_id = agent_repository.create_agent(
        name="Failed Reviewer Agent",
        role="worker",
    )

    task_id = service.create_task(
        title="Failed review returns to running task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        service.record_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            result="fail",
            findings=["Issues detected."],
        )

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "running"

    finally:
        service.repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)


def test_passing_review_allows_completion():
    service = TaskService()
    agent_repository = AgentRepository()

    reviewer_id = agent_repository.create_agent(
        name="Passing Reviewer Agent",
        role="worker",
    )

    task_id = service.create_task(
        title="Passing review task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        service.record_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            result="pass",
            report="Everything looks great.",
        )

        service.transition_task(task_id, "completed")

        task = service.repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "completed"
        assert task["completed_at"] is not None

    finally:
        service.repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)


def test_completion_without_review_is_rejected():
    service = TaskService()

    task_id = service.create_task(
        title="No review completion rejection task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        with pytest.raises(
            ValueError,
            match="Task requires a review before completion",
        ):
            service.transition_task(task_id, "completed")

    finally:
        service.repository.delete_task(task_id)


def test_multiple_review_attempts_are_preserved():
    service = TaskService()
    agent_repository = AgentRepository()

    reviewer_id = agent_repository.create_agent(
        name="Multi Review Agent",
        role="worker",
    )

    task_id = service.create_task(
        title="Multi review attempt task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        # Attempt 1: fail
        service.record_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            result="fail",
            findings=["First attempt failed"],
        )

        task = service.repository.get_task(task_id)
        assert task["status"] == "running"

        # Resume to review
        service.transition_task(task_id, "review")

        # Attempt 2: pass
        service.record_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            result="pass",
            report="Second attempt succeeded",
        )

        reviews = service.get_reviews(task_id)
        assert len(reviews) == 2
        assert reviews[0]["attempt_number"] == 1
        assert reviews[0]["result"] == "fail"
        assert reviews[1]["attempt_number"] == 2
        assert reviews[1]["result"] == "pass"

    finally:
        service.repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)


def test_latest_review_determines_whether_completion_is_allowed():
    service = TaskService()
    agent_repository = AgentRepository()

    reviewer_id = agent_repository.create_agent(
        name="Latest Review Determinant Agent",
        role="worker",
    )

    task_id = service.create_task(
        title="Latest review determines completion task",
        requires_review=True,
    )

    try:
        service.transition_task(task_id, "planned")
        service.transition_task(task_id, "assigned")
        service.transition_task(task_id, "running")
        service.transition_task(task_id, "review")

        # Attempt 1: fail
        service.record_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            result="fail",
        )

        # It's now running, cannot complete directly
        with pytest.raises(
            ValueError,
            match="Task requires review before completion",
        ):
            service.transition_task(task_id, "completed")

        # Return to review
        service.transition_task(task_id, "review")

        # Attempt 2: pass
        service.record_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            result="pass",
        )

        # Now completion is allowed
        service.transition_task(task_id, "completed")

        task = service.repository.get_task(task_id)
        assert task["status"] == "completed"

    finally:
        service.repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)
