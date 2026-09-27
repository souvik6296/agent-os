from core.repositories.agents import AgentRepository
from core.repositories.tasks import TaskRepository


def test_task_repository_creates_and_reads_task():
    repository = TaskRepository()

    task_id = repository.create_task(
        title="Repository test task",
        description="Testing task creation.",
        priority="high",
        input_data={
            "source": "test",
            "value": 123,
        },
        metadata={
            "test": True,
        },
    )

    try:
        task = repository.get_task(task_id)

        assert task is not None
        assert str(task["id"]) == task_id
        assert task["title"] == "Repository test task"
        assert task["description"] == "Testing task creation."
        assert task["status"] == "created"
        assert task["priority"] == "high"
        assert task["input_data"]["value"] == 123
        assert task["metadata"]["test"] is True

    finally:
        repository.delete_task(task_id)


def test_task_repository_updates_status():
    repository = TaskRepository()

    task_id = repository.create_task(
        title="Status test task",
    )

    try:
        repository.update_status(
            task_id=task_id,
            status="running",
        )

        task = repository.get_task(task_id)

        assert task is not None
        assert task["status"] == "running"

    finally:
        repository.delete_task(task_id)


def test_task_repository_assigns_agent():
    task_repository = TaskRepository()
    agent_repository = AgentRepository()

    task_id = task_repository.create_task(
        title="Agent assignment test",
    )

    agent_id = agent_repository.create_agent(
        name="task-repository-test-agent",
        role="worker",
    )

    try:
        task_repository.assign_agent(
            task_id=task_id,
            agent_id=agent_id,
        )

        task = task_repository.get_task(task_id)

        assert task is not None
        assert str(task["assigned_agent_id"]) == agent_id
        assert task["assigned_team_id"] is None

    finally:
        task_repository.delete_task(task_id)
        agent_repository.delete_agent(agent_id)


def test_task_repository_updates_output():
    repository = TaskRepository()

    task_id = repository.create_task(
        title="Output test task",
    )

    try:
        repository.update_output(
            task_id=task_id,
            output_data={
                "result": "success",
                "count": 42,
            },
        )

        task = repository.get_task(task_id)

        assert task is not None
        assert task["output_data"]["result"] == "success"
        assert task["output_data"]["count"] == 42

    finally:
        repository.delete_task(task_id)


def test_task_repository_lists_tasks_by_status():
    repository = TaskRepository()

    first_task_id = repository.create_task(
        title="List test one",
        status="planned",
    )

    second_task_id = repository.create_task(
        title="List test two",
        status="planned",
    )

    third_task_id = repository.create_task(
        title="List test three",
        status="created",
    )

    try:
        planned_tasks = repository.list_tasks(
            status="planned",
        )

        planned_ids = {
            str(task["id"])
            for task in planned_tasks
        }

        assert first_task_id in planned_ids
        assert second_task_id in planned_ids
        assert third_task_id not in planned_ids

    finally:
        repository.delete_task(first_task_id)
        repository.delete_task(second_task_id)
        repository.delete_task(third_task_id)
