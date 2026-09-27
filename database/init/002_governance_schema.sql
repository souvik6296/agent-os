-- ============================================================
-- Agent OS
-- Governance & Audit Schema
-- Version 0.1
-- ============================================================


-- ============================================================
-- PERMISSIONS
-- ============================================================

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT,

    risk_level VARCHAR(20) NOT NULL DEFAULT 'low',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT permissions_risk_check
        CHECK (risk_level IN (
            'low',
            'medium',
            'high',
            'critical'
        ))
);


-- ============================================================
-- AGENT PERMISSIONS
-- ============================================================

CREATE TABLE agent_permissions (
    agent_id UUID NOT NULL
        REFERENCES agents(id) ON DELETE CASCADE,

    permission_id UUID NOT NULL
        REFERENCES permissions(id) ON DELETE CASCADE,

    granted_by_agent_id UUID
        REFERENCES agents(id) ON DELETE SET NULL,

    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    expires_at TIMESTAMPTZ,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    PRIMARY KEY (agent_id, permission_id)
);


-- ============================================================
-- GOVERNANCE REQUESTS
-- ============================================================

CREATE TABLE governance_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    agent_id UUID NOT NULL
        REFERENCES agents(id) ON DELETE RESTRICT,

    task_id UUID
        REFERENCES tasks(id) ON DELETE SET NULL,

    action VARCHAR(150) NOT NULL,

    resource VARCHAR(300) NOT NULL,

    requested_permissions JSONB NOT NULL DEFAULT '[]'::jsonb,

    context JSONB NOT NULL DEFAULT '{}'::jsonb,

    status VARCHAR(30) NOT NULL DEFAULT 'pending',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT governance_request_status_check
        CHECK (status IN (
            'pending',
            'approved',
            'denied',
            'expired'
        ))
);


-- ============================================================
-- GOVERNANCE DECISIONS
-- ============================================================

CREATE TABLE governance_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    request_id UUID NOT NULL
        REFERENCES governance_requests(id) ON DELETE CASCADE,

    decision VARCHAR(20) NOT NULL,

    policy_id VARCHAR(150),

    reason TEXT NOT NULL,

    evaluator VARCHAR(50) NOT NULL DEFAULT 'deterministic',

    evaluation_data JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT governance_decision_check
        CHECK (decision IN (
            'ALLOW',
            'DENY',
            'ESCALATE'
        ))
);


-- ============================================================
-- AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    agent_id UUID
        REFERENCES agents(id) ON DELETE SET NULL,

    task_id UUID
        REFERENCES tasks(id) ON DELETE SET NULL,

    governance_request_id UUID
        REFERENCES governance_requests(id) ON DELETE SET NULL,

    action VARCHAR(150) NOT NULL,

    resource VARCHAR(300),

    result VARCHAR(50),

    details JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_agent_permissions_agent
    ON agent_permissions(agent_id);

CREATE INDEX idx_agent_permissions_permission
    ON agent_permissions(permission_id);

CREATE INDEX idx_governance_requests_agent
    ON governance_requests(agent_id);

CREATE INDEX idx_governance_requests_task
    ON governance_requests(task_id);

CREATE INDEX idx_governance_requests_status
    ON governance_requests(status);

CREATE INDEX idx_governance_decisions_request
    ON governance_decisions(request_id);

CREATE INDEX idx_audit_logs_agent
    ON audit_logs(agent_id);

CREATE INDEX idx_audit_logs_task
    ON audit_logs(task_id);

CREATE INDEX idx_audit_logs_governance_request
    ON audit_logs(governance_request_id);

CREATE INDEX idx_audit_logs_created
    ON audit_logs(created_at);