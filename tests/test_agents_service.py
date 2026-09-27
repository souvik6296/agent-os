import pytest

from core.database.connection import get_connection
from core.repositories.agents import AgentRepository
from core.services.agents import AgentService
from core.repositories.permissions import PermissionRepository


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

def test_agent_service_denies_creation_without_permission():
    service = AgentService()

    creator_id = service.create_agent(
        name="permission-test-worker",
        role="worker",
    )

    try:
        with pytest.raises(
            PermissionError,
            match="Required permission",
        ):
            service.create_agent(
                name="unauthorized-worker",
                role="worker",
                creator_agent_id=creator_id,
                creator_role="worker",
            )

    finally:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM audit_logs
                    WHERE agent_id = %s;
                    """,
                    (creator_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_decisions
                    WHERE request_id IN (
                        SELECT id
                        FROM governance_requests
                        WHERE agent_id = %s
                    );
                    """,
                    (creator_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_requests
                    WHERE agent_id = %s;
                    """,
                    (creator_id,),
                )

            connection.commit()

        service.repository.delete_agent(creator_id)


def test_agent_service_allows_creation_with_permission():
    service = AgentService()
    permission_repository = PermissionRepository()

    creator_id = service.create_agent(
        name="authorized-manager",
        role="manager",
    )

    permission_id = permission_repository.create_permission(
        name="AGENT_CREATE",
        description="Allows an authorized agent to create another agent.",
        risk_level="high",
    )

    permission_repository.grant_permission(
        agent_id=creator_id,
        permission_id=permission_id,
    )

    child_id = None

    try:
        child_id = service.create_agent(
            name="authorized-worker",
            role="worker",
            creator_agent_id=creator_id,
            creator_role="manager",
            parent_agent_id=creator_id,
        )

        child = service.repository.get_agent(child_id)

        assert child is not None
        assert str(child["parent_agent_id"]) == creator_id

    finally:
        if child_id:
            service.repository.delete_agent(child_id)

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM audit_logs
                    WHERE agent_id = %s;
                    """,
                    (creator_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_decisions
                    WHERE request_id IN (
                        SELECT id
                        FROM governance_requests
                        WHERE agent_id = %s
			);
                    """,
                    (creator_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM governance_requests
                    WHERE agent_id = %s;
                    """,
                    (creator_id,),
                )

                cursor.execute(
                    """
                    DELETE FROM agent_permissions
                    WHERE agent_id = %s;
                    """,
                    (creator_id,),
                )

            connection.commit()

        service.repository.delete_agent(creator_id)