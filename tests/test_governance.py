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