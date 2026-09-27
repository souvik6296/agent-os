from typing import Any

from core.repositories.agents import AgentRepository


class AgentService:
    """
    Handles agent lifecycle operations above the persistence layer.
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
    ):
        self.repository = repository or AgentRepository()

    def create_agent(
        self,
        name: str,
        role: str,
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

        return self.repository.create_agent(
            name=name,
            role=role,
            parent_agent_id=parent_agent_id,
            model_provider=model_provider,
            model_name=model_name,
            system_prompt=system_prompt,
            metadata=metadata,
        )