-- ============================================================
-- Agent OS
-- Core Database Schema
-- Version 0.1
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;


-- ============================================================
-- AGENTS
-- ============================================================

CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,

    parent_agent_id UUID REFERENCES agents(id),

    status VARCHAR(30) NOT NULL DEFAULT 'active',

    model_provider VARCHAR(50),
    model_name VARCHAR(100),

    system_prompt TEXT,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT agents_status_check
        CHECK (status IN (
            'active',
            'inactive',
            'suspended',
            'terminated'
        ))
);


-- ============================================================
-- TEAMS
-- ============================================================

CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(150) NOT NULL UNIQUE,

    manager_agent_id UUID REFERENCES agents(id),

    description TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'active',

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT teams_status_check
        CHECK (status IN (
            'active',
            'inactive',
            'archived'
        ))
);


-- ============================================================
-- AGENT ↔ TEAM MEMBERSHIP
-- ============================================================

CREATE TABLE agent_team_memberships (
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,

    membership_role VARCHAR(50) NOT NULL DEFAULT 'member',

    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (agent_id, team_id)
);


-- ============================================================
-- PROJECTS
-- ============================================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(200) NOT NULL,

    description TEXT,

    owner_agent_id UUID REFERENCES agents(id),

    status VARCHAR(30) NOT NULL DEFAULT 'active',

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT projects_status_check
        CHECK (status IN (
            'planned',
            'active',
            'paused',
            'completed',
            'cancelled'
        ))
);


-- ============================================================
-- TASKS
-- ============================================================

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

    assigned_agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,

    assigned_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,

    title VARCHAR(300) NOT NULL,

    description TEXT,

    status VARCHAR(30) NOT NULL DEFAULT 'created',

    priority VARCHAR(20) NOT NULL DEFAULT 'normal',

    input_data JSONB NOT NULL DEFAULT '{}'::jsonb,

    output_data JSONB NOT NULL DEFAULT '{}'::jsonb,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT tasks_status_check
        CHECK (status IN (
            'created',
            'planned',
            'assigned',
            'running',
            'waiting',
            'review',
            'completed',
            'failed',
            'cancelled'
        )),

    CONSTRAINT tasks_priority_check
        CHECK (priority IN (
            'low',
            'normal',
            'high',
            'critical'
        ))
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_agents_parent
    ON agents(parent_agent_id);

CREATE INDEX idx_agents_role
    ON agents(role);

CREATE INDEX idx_agents_status
    ON agents(status);

CREATE INDEX idx_team_manager
    ON teams(manager_agent_id);

CREATE INDEX idx_tasks_project
    ON tasks(project_id);

CREATE INDEX idx_tasks_agent
    ON tasks(assigned_agent_id);

CREATE INDEX idx_tasks_team
    ON tasks(assigned_team_id);

CREATE INDEX idx_tasks_status
    ON tasks(status);

CREATE INDEX idx_tasks_parent
    ON tasks(parent_task_id);