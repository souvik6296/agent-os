from typing import Any

from core.repositories.agents import AgentRepository
from core.services.governance import GovernanceService


class AgentService:
    """
    Handles governed agent lifecycle operations.
    """

    VALID_ROLES = {
        "owner",
        "boss",
        "manager",
        "team",
        "worker",
    }

    def __init__(
        self,
        repository: AgentRepository | None = None,
        governance_service: GovernanceService | None = None,
    ):
        self.repository = repository or AgentRepository()
        self.governance_service = (
            governance_service or GovernanceService()
        )

    def bootstrap_owner(
        self,
        name: str,
        model_provider: str | None = None,
        model_name: str | None = None,
        system_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if not name.strip():
            raise ValueError("Agent name cannot be empty.")

        existing_owner = self.repository.get_owner()

        if existing_owner is not None:
            raise ValueError("Owner agent already exists.")

        return self.repository.create_agent(
            name=name,
            role="owner",
            parent_agent_id=None,
            model_provider=model_provider,
            model_name=model_name,
            system_prompt=system_prompt,
            metadata=metadata,
        )

    def create_agent(
        self,
        name: str,
        role: str,
        creator_agent_id: str | None = None,
        creator_role: str | None = None,
        parent_agent_id: str | None = None,
        model_provider: str | None = None,
        model_name: str | None = None,
        system_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if not name.strip():
            raise ValueError("Agent name cannot be empty.")

        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid agent role: {role}")

        if role == "owner" and parent_agent_id is not None:
            raise ValueError("Owner cannot have a parent agent.")

        if parent_agent_id is not None:
            parent = self.repository.get_agent(parent_agent_id)

            if parent is None:
                raise ValueError("Parent agent does not exist.")

        # Agent creation is a governed operation.
        if creator_agent_id is not None:
            if creator_role is None:
                raise ValueError(
                    "Creator role is required when creator agent is provided."
                )

            governance_result = self.governance_service.authorize(
                agent_id=creator_agent_id,
                role=creator_role,
                action="create_agent",
                resource="agent",
                requested_permissions=["AGENT_CREATE"],
                context={
                    "target_role": role,
                },
            )

            if governance_result["decision"] != "ALLOW":
                raise PermissionError(
                    governance_result["reason"]
                )

        return self.repository.create_agent(
            name=name,
            role=role,
            parent_agent_id=parent_agent_id,
            model_provider=model_provider,
            model_name=model_name,
            system_prompt=system_prompt,
            metadata=metadata,
        )