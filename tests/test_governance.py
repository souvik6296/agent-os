from core.governance.engine import GovernanceEngine, GovernanceRequest


engine = GovernanceEngine()


def test_normal_action_is_allowed():
    request = GovernanceRequest(
        agent_id="worker-001",
        role="worker",
        action="create_file",
        resource="project_workspace",
        context={},
    )

    decision = engine.evaluate(request)

    assert decision.decision == "ALLOW"


def test_worker_cannot_modify_constitution():
    request = GovernanceRequest(
        agent_id="worker-001",
        role="worker",
        action="modify",
        resource="constitution",
        context={},
    )

    decision = engine.evaluate(request)

    assert decision.decision == "DENY"


def test_security_violation_is_denied():
    request = GovernanceRequest(
        agent_id="worker-001",
        role="worker",
        action="execute",
        resource="system",
        context={
            "security_violation": True,
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "DENY"


def test_owner_can_create_boss():
    request = GovernanceRequest(
        agent_id="owner-001",
        role="owner",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "boss",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "ALLOW"
    assert decision.policy == "autonomous_action"


def test_boss_can_create_manager():
    request = GovernanceRequest(
        agent_id="boss-001",
        role="boss",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "manager",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "ALLOW"


def test_manager_can_create_team():
    request = GovernanceRequest(
        agent_id="manager-001",
        role="manager",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "team",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "ALLOW"


def test_manager_can_create_worker():
    request = GovernanceRequest(
        agent_id="manager-001",
        role="manager",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "worker",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "ALLOW"


def test_team_can_create_worker():
    request = GovernanceRequest(
        agent_id="team-001",
        role="team",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "worker",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "ALLOW"


def test_worker_cannot_create_agent():
    request = GovernanceRequest(
        agent_id="worker-001",
        role="worker",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "worker",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "DENY"
    assert decision.policy == "hierarchy_authority"


def test_manager_cannot_create_manager():
    request = GovernanceRequest(
        agent_id="manager-001",
        role="manager",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "manager",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "DENY"
    assert decision.policy == "hierarchy_authority"


def test_boss_cannot_create_worker_directly():
    request = GovernanceRequest(
        agent_id="boss-001",
        role="boss",
        action="create_agent",
        resource="agent",
        context={
            "target_role": "worker",
        },
    )

    decision = engine.evaluate(request)

    assert decision.decision == "DENY"
    assert decision.policy == "hierarchy_authority"
