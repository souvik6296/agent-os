from core.repositories.agents import AgentRepository
from core.repositories.tasks import TaskRepository
from core.repositories.task_reviews import TaskReviewRepository


def test_create_and_get_review():
    agent_repository = AgentRepository()
    task_repository = TaskRepository()
    review_repository = TaskReviewRepository()

    reviewer_id = agent_repository.create_agent(
        name="Review Test Agent",
        role="worker",
    )

    task_id = task_repository.create_task(
        title="Review repository test task",
        requires_review=True,
    )

    try:
        review_id = review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            attempt_number=1,
            result="pass",
            test_cases=[
                {
                    "name": "basic requirement test",
                    "expected": "pass",
                }
            ],
            test_results={
                "passed": 1,
                "failed": 0,
            },
            findings=[],
            report="All requirements passed.",
        )

        review = review_repository.get_review(review_id)

        assert review is not None
        assert str(review["id"]) == review_id
        assert str(review["task_id"]) == task_id
        assert str(review["reviewer_agent_id"]) == reviewer_id
        assert review["attempt_number"] == 1
        assert review["result"] == "pass"
        assert review["test_results"]["passed"] == 1
        assert review["findings"] == []
        assert review["completed_at"] is not None

    finally:
        task_repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)


def test_list_reviews_returns_attempts_in_order():
    agent_repository = AgentRepository()
    task_repository = TaskRepository()
    review_repository = TaskReviewRepository()

    reviewer_id = agent_repository.create_agent(
        name="Review History Agent",
        role="worker",
    )

    task_id = task_repository.create_task(
        title="Review history test task",
        requires_review=True,
    )

    try:
        review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            attempt_number=1,
            result="fail",
            findings=["Requirement not satisfied."],
        )

        review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            attempt_number=2,
            result="pass",
            findings=[],
        )

        reviews = review_repository.list_reviews(task_id)

        assert len(reviews) == 2
        assert reviews[0]["attempt_number"] == 1
        assert reviews[0]["result"] == "fail"
        assert reviews[1]["attempt_number"] == 2
        assert reviews[1]["result"] == "pass"

    finally:
        task_repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)


def test_get_latest_review_returns_latest_attempt():
    agent_repository = AgentRepository()
    task_repository = TaskRepository()
    review_repository = TaskReviewRepository()

    reviewer_id = agent_repository.create_agent(
        name="Latest Review Agent",
        role="worker",
    )

    task_id = task_repository.create_task(
        title="Latest review test task",
        requires_review=True,
    )

    try:
        review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            attempt_number=1,
            result="fail",
        )

        review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            attempt_number=2,
            result="pass",
        )

        latest = review_repository.get_latest_review(task_id)

        assert latest is not None
        assert latest["attempt_number"] == 2
        assert latest["result"] == "pass"

    finally:
        task_repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)


def test_delete_review():
    agent_repository = AgentRepository()
    task_repository = TaskRepository()
    review_repository = TaskReviewRepository()

    reviewer_id = agent_repository.create_agent(
        name="Delete Review Agent",
        role="worker",
    )

    task_id = task_repository.create_task(
        title="Delete review test task",
    )

    try:
        review_id = review_repository.create_review(
            task_id=task_id,
            reviewer_agent_id=reviewer_id,
            attempt_number=1,
            result="pass",
        )

        assert review_repository.get_review(review_id) is not None

        review_repository.delete_review(review_id)

        assert review_repository.get_review(review_id) is None

    finally:
        task_repository.delete_task(task_id)
        agent_repository.delete_agent(reviewer_id)
