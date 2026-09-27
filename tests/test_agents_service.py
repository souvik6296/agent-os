import pytest

from core.database.connection import get_connection
from core.repositories.agents import AgentRepository
from core.services.agents import AgentService


def test_agent_service_creates_valid_agent():
    service = AgentService()

    agent_id = service.create_agent(
        name="service-test-worker",
        role="worker",
        model_provider="ollama",
        model_name="qwen3:8b",
        system_prompt="You are a test worker.",
        metadata={"test": True},
    )

    try:
        agent = service.repository.get_agent(agent_id)

        assert agent is not None
        assert str(agent["id"]) == agent_id
        assert agent["name"] == "service-test-worker"
        assert agent["role"] == "worker"
        assert agent["status"] == "active"

    finally:
        service.repository.delete_agent(agent_id)


def test_agent_service_rejects_invalid_role():
    service = AgentService()

    with pytest.raises(ValueError, match="Invalid agent role"):
        service.create_agent(
            name="invalid-role-agent",
            role="random_role",
        )


def test_agent_service_rejects_empty_name():
    service = AgentService()

    with pytest.raises(ValueError, match="Agent name cannot be empty"):
        service.create_agent(
            name="   ",
            role="worker",
        )


def test_agent_service_rejects_owner_with_parent():
    service = AgentService()

    parent_id = service.create_agent(
        name="service-test-parent",
        role="boss",
    )

    try:
        with pytest.raises(
            ValueError,
            match="Owner cannot have a parent agent",
        ):
            service.create_agent(
                name="invalid-owner",
                role="owner",
                parent_agent_id=parent_id,
            )

    finally:
        service.repository.delete_agent(parent_id)


def test_agent_service_rejects_missing_parent():
    service = AgentService()

    missing_parent_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(
        ValueError,
        match="Parent agent does not exist",
    ):
        service.create_agent(
            name="orphan-worker",
            role="worker",
            parent_agent_id=missing_parent_id,
        )