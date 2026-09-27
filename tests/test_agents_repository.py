from core.database.connection import get_connection
from core.repositories.agents import AgentRepository


def test_agent_repository_create_get_update_and_delete():
    repository = AgentRepository()

    agent_id = repository.create_agent(
        name="repository-test-worker",
        role="worker",
        model_provider="ollama",
        model_name="qwen3:8b",
        system_prompt="You are a test worker.",
        metadata={"test": True},
    )

    try:
        agent = repository.get_agent(agent_id)

        assert agent is not None
        assert str(agent["id"]) == agent_id
        assert agent["name"] == "repository-test-worker"
        assert agent["role"] == "worker"
        assert agent["status"] == "active"
        assert agent["model_provider"] == "ollama"
        assert agent["model_name"] == "qwen3:8b"
        assert agent["metadata"]["test"] is True

        repository.update_status(
            agent_id,
            "suspended",
        )

        agent = repository.get_agent(agent_id)

        assert agent["status"] == "suspended"

        parent_id = repository.create_agent(
            name="repository-test-manager",
            role="manager",
        )

        try:
            repository.assign_parent(
                agent_id,
                parent_id,
            )

            agent = repository.get_agent(agent_id)

            assert str(agent["parent_agent_id"]) == parent_id

        finally:
            repository.assign_parent(
                agent_id,
                None,
            )
            repository.delete_agent(parent_id)

    finally:
        repository.delete_agent(agent_id)


def test_agent_repository_get_missing_agent_returns_none():
    repository = AgentRepository()

    missing_agent_id = "00000000-0000-0000-0000-000000000000"

    result = repository.get_agent(missing_agent_id)

    assert result is None