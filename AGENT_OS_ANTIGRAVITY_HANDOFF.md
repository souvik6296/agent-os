# Agent OS — Master Handoff / Build Prompt

> **Purpose:** This document is the single handoff prompt for continuing Agent OS development in Antigravity. Read it completely before changing the codebase.
>
> **Current stage:** Foundation + task/review infrastructure is implemented. The next priority is to finish review enforcement and then build the first real autonomous agent execution loop.

---

# 1. PROJECT GOAL

We are building **Agent OS**, a hierarchical autonomous AI organization.

The intended organization is:

```text
OWNER / HUMAN
      │
      ▼
    BOSS
      │
      ▼
  MANAGERS
      │
      ▼
    TEAMS
      │
      ▼
   WORKERS
      │
      ▼
 TOOLS / MCP
```

The human is the ultimate authority, but normal operation should be autonomous.

The system should eventually allow:

1. Human gives the organization a legitimate objective.
2. Boss understands the objective and creates a plan.
3. Boss delegates to managers.
4. Managers create teams/work and assign workers.
5. Workers execute tasks using approved tools.
6. Agents communicate with each other.
7. Important work is reviewed by another AI agent/supervisor.
8. Failed work goes back for correction.
9. Successful work is completed automatically.
10. Everything important is auditable.
11. Agents maintain useful memory.
12. Agents can create meetings and minutes.
13. If a required capability/tool does not exist, an agent can eventually:
    - identify the missing capability,
    - generate the implementation,
    - test it in a sandbox,
    - run security/static checks,
    - request/evaluate governance approval,
    - register a version,
    - use the capability.
14. Agents can eventually propose self-improvements:
    - proposal,
    - tests/benchmarks,
    - governance evaluation,
    - deployment,
    - monitoring,
    - rollback if necessary.

The system should NOT require human approval for every ordinary autonomous action.

Instead, the **Constitution + Governance Engine** should determine whether an action is allowed.

Human remains the ultimate authority and emergency override.

---

# 2. CORE DESIGN PRINCIPLES

## 2.1 Model vs Agent

A model is the brain.

An agent is:

```text
MODEL
+
GOAL
+
SYSTEM INSTRUCTIONS
+
DECISION LOOP
+
TOOLS
+
MEMORY
+
PERMISSIONS
+
RUNTIME
```

Do not treat an LLM itself as the complete agent.

---

## 2.2 MCP

MCP is a standardized mechanism for exposing tools/resources to agents.

MCP is NOT itself the tool.

Eventually Agent OS should have an MCP/tool registry.

---

## 2.3 Model Gateway

Do not tightly couple Agent OS to Ollama.

Create a model gateway abstraction so the system can initially use:

```text
Ollama / qwen3:8b
```

but later swap to cloud or other models without rewriting the agent runtime.

Example conceptual interface:

```text
ModelGateway
    ├── OllamaGateway
    ├── OpenAIGateway
    ├── AnthropicGateway
    └── other providers later
```

---

## 2.4 Logs vs Memory

Do not treat all logs as memory.

Logs are event/audit history.

Memory is useful persistent information.

Worker logs can later be summarized:

```text
Worker
  ↓ summary
Team
  ↓ summary
Manager
  ↓ summary
Boss
```

But drill-down should remain possible.

---

## 2.5 Dynamic Agents

Do not run hundreds of agents permanently.

Prefer dynamic/ephemeral execution:

```text
Task
 ↓
create/activate required agent
 ↓
execute
 ↓
finish
 ↓
agent can become inactive
```

---

# 3. TECHNOLOGY STACK

Current direction:

```text
Python backend
PostgreSQL
pgvector
Docker
Git/GitHub
Ollama
Next.js dashboard later
```

Current local machine:

```text
MacBook Air
Apple Silicon M4
16 GB unified memory
```

Ollama is installed.

Current local model:

```text
qwen3:8b
```

Docker is working.

PostgreSQL is running in Docker using:

```text
pgvector/pgvector:pg17
```

Current database:

```text
database: agent_os
user: agent_os
password: agent_os_dev
port: 5432
container: agent-os-postgres
```

---

# 4. REPOSITORY STRUCTURE

Current intended structure:

```text
agent-os/
│
├── core/
│   ├── database/
│   ├── governance/
│   ├── repositories/
│   └── services/
│
├── agents/
│
├── governance/
│   └── policies/
│
├── capabilities/
│   └── generated/
│
├── sandbox/
│
├── database/
│   └── init/
│
├── dashboard/
│
├── tests/
│
└── docs/
```

Important principle:

Agents may eventually generate code under controlled capability areas such as:

```text
capabilities/generated/
```

They must NOT arbitrarily rewrite core governance/identity/audit systems.

---

# 5. CONSTITUTION

A Constitution v0.1 has already been designed.

Core articles:

1. Mission
2. Hierarchy
3. Autonomy
4. Governance
5. Core Protection
6. Least Authority
7. Audit
8. Capability Creation
9. Self-Improvement
10. Communication / Meetings
11. Memory
12. Resource Governance
13. Security
14. Reversibility
15. Failure
16. Human Authority
17. Interpretation
18. Amendment
19. Auditability
20. Core Principle

Machine-readable policies exist at:

```text
governance/policies/core.yaml
```

---

# 6. GOVERNANCE MODEL

The Governance Engine is deterministic.

Current implementation:

```text
core/governance/engine.py
```

It evaluates:

- protected resources
- permissions
- hierarchy authority
- least authority
- resource limits
- security
- audit availability
- rollback/reversibility

Core protected resources:

```text
constitution
governance_engine
root_identity
root_permissions
audit_system
```

Ordinary agents cannot modify those resources.

Owner is allowed to modify protected core resources.

---

# 7. AGENT HIERARCHY

Allowed hierarchy:

```text
Owner → Boss
Boss → Manager
Manager → Team
Manager → Worker
Team → Worker
Worker → nothing
```

Current governance tests verify:

- owner can create boss
- boss can create manager
- manager can create team
- manager can create worker
- team can create worker
- worker cannot create agents
- manager cannot create manager
- boss cannot directly create worker

There is also a single-owner database invariant.

---

# 8. CURRENT DATABASE

## 8.1 Agents

`agents` table contains:

```text
id
name
role
parent_agent_id
status
model_provider
model_name
system_prompt
metadata
created_at
updated_at
```

Roles:

```text
owner
boss
manager
team
worker
```

Statuses:

```text
active
inactive
suspended
terminated
```

A partial unique index enforces a single owner.

---

# 9. PERMISSIONS

Permission infrastructure exists.

Tables:

```text
permissions
agent_permissions
```

Current permission:

```text
AGENT_CREATE
```

It is a high-risk permission.

It should NOT be globally granted.

Permission checks are integrated into governance authorization.

---

# 10. GOVERNANCE DATABASE

`database/init/002_governance_schema.sql`

Contains:

```text
permissions
agent_permissions
governance_requests
governance_decisions
audit_logs
```

Governance service:

```text
core/services/governance.py
```

Current flow:

```text
Agent action
    ↓
GovernanceService.authorize()
    ↓
GovernanceRepository
    ↓
GovernanceEngine
    ↓
ALLOW / DENY
    ↓
Decision persisted
    ↓
Audit persisted
```

---

# 11. AGENT SERVICES / REPOSITORIES

Current files include:

```text
core/repositories/agents.py
core/repositories/governance.py
core/repositories/permissions.py
core/repositories/tasks.py

core/services/governance.py
core/services/tasks.py

core/governance/engine.py
```

AgentService exists and handles:

- owner bootstrap
- agent creation
- role validation
- parent validation
- governance authorization

Important temporary caveat:

```text
creator_agent_id=None
```

can currently bypass creator governance in the generic creation method.

This should be tightened before production/MVP hardening.

`bootstrap_owner()` is intentionally the explicit root bootstrap path.

---

# 12. TASK SYSTEM

Task database table exists.

Important fields:

```text
id
project_id
parent_task_id
assigned_agent_id
assigned_team_id
title
description
status
priority
input_data
output_data
metadata
requires_review
created_at
started_at
completed_at
updated_at
```

Statuses:

```text
created
planned
assigned
running
waiting
review
completed
failed
cancelled
```

Priorities:

```text
low
normal
high
critical
```

---

# 13. TASK LIFECYCLE

Current intended lifecycle:

```text
CREATED
   ↓
PLANNED
   ↓
ASSIGNED
   ↓
RUNNING
   ├──→ WAITING ──→ RUNNING
   │
   ├──→ COMPLETED
   │
   ├──→ REVIEW
   │      ├── pass → COMPLETED
   │      └── fail → RUNNING
   │
   ├──→ FAILED
   │
   └──→ CANCELLED
```

Active states can be cancelled.

Review should normally be performed by a separate AI supervisor, not necessarily a human.

---

# 14. TASK REPOSITORY

Current file:

```text
core/repositories/tasks.py
```

It supports:

```text
create_task()
get_task()
list_tasks()
update_status()
assign_agent()
assign_team()
update_output()
delete_task()
```

It now supports:

```text
requires_review
```

and lifecycle timestamps.

Repository tests:

```text
tests/test_tasks_repository.py
```

Current result:

```text
5 passed
```

---

# 15. TASK SERVICE

Current file:

```text
core/services/tasks.py
```

It handles:

- task creation
- title validation
- priority validation
- valid lifecycle transitions
- review-required completion protection

Current service tests:

```text
tests/test_tasks_service.py
```

Current result:

```text
12 passed
```

Important current limitation:

The service currently allows:

```text
review → completed
```

without checking whether a recorded review actually passed.

This MUST be fixed next.

---

# 16. TASK REVIEW DATABASE

Migration:

```text
database/init/003_task_review_schema.sql
```

Added:

```text
tasks.requires_review
```

and created:

```text
task_reviews
```

`task_reviews` fields:

```text
id
task_id
reviewer_agent_id
attempt_number
result
test_cases
test_results
findings
report
created_at
completed_at
```

Constraints:

```text
attempt_number > 0
result ∈ {pass, fail}
UNIQUE(task_id, attempt_number)
```

Foreign keys:

```text
task_id → tasks
reviewer_agent_id → agents
```

---

# 17. TASK REVIEW REPOSITORY

Current file:

```text
core/repositories/task_reviews.py
```

Methods:

```text
create_review()
get_review()
list_reviews()
get_latest_review()
delete_review()
```

Tests:

```text
tests/test_task_reviews_repository.py
```

Current result:

```text
4 passed
```

---

# 18. CURRENT TEST STATE

Latest known focused results:

```text
TaskRepository:
5 passed

TaskService:
12 passed

TaskReviewRepository:
4 passed
```

The full test suite currently cannot complete because the implementation had just been created progressively; after the current changes, run:

```bash
python -m pytest
```

Do NOT use bare:

```bash
pytest
```

because the machine's PATH currently resolves a global pytest executable.

Use:

```bash
python -m pytest
```

to guarantee the virtual environment's Python.

---

# 19. IMMEDIATE NEXT STEP

## Finish review enforcement.

We need to connect:

```text
TaskService
+
TaskReviewRepository
```

so that:

```text
requires_review = true
```

means:

```text
RUNNING
 ↓
REVIEW
 ↓
record review
 ↓
if PASS:
    COMPLETED
if FAIL:
    RUNNING
```

A review-required task must NOT be allowed to go:

```text
RUNNING → COMPLETED
```

without a valid passing review.

Likewise:

```text
REVIEW → COMPLETED
```

should require the latest review to have:

```text
result = "pass"
```

Add tests for:

1. review-required task cannot directly complete
2. review-required task enters review
3. failed review returns task to running
4. passing review allows completion
5. completion without review is rejected
6. multiple review attempts are preserved
7. latest review determines whether completion is allowed

Do this before building the agent runtime.

---

# 20. FIRST MVP DEFINITION

The first MVP is NOT the full self-improving AI society.

The first MVP should prove one complete autonomous loop:

```text
HUMAN
  ↓
BOSS AGENT
  ↓
PLAN
  ↓
MANAGER
  ↓
WORKER
  ↓
MODEL
  ↓
APPROVED TOOL
  ↓
RESULT
  ↓
AI REVIEWER
  ↓
TESTS
  ↓
PASS
  ↓
COMPLETED
```

Everything important should be persisted.

The human should be able to see:

```text
task
who created it
who delegated it
who executed it
agent actions
tools used
review attempts
review findings
final result
audit trail
```

---

# 21. MVP REMAINING WORK

After review enforcement:

## Phase A — Model Gateway

Build:

```text
core/models/
```

with an abstraction such as:

```text
ModelGateway
```

Initial implementation:

```text
OllamaGateway
```

using:

```text
qwen3:8b
```

The rest of Agent OS should not directly call Ollama APIs.

---

## Phase B — Agent Runtime

Build the first actual agent execution loop.

Conceptually:

```text
Agent
 ↓
receive task
 ↓
read context
 ↓
reason
 ↓
choose action
 ↓
governance check
 ↓
execute tool/action
 ↓
observe result
 ↓
continue / finish
```

Do not implement uncontrolled arbitrary code execution.

All actions should go through governed capabilities/tools.

---

# 22. PHASE C — TOOL RUNTIME

Create a controlled tool system.

Conceptually:

```text
Tool Registry
     ↓
Tool Definition
     ↓
Permissions
     ↓
Governance
     ↓
Tool Runtime
     ↓
Execution
     ↓
Audit
```

Initial tools should be minimal.

Examples:

```text
filesystem read/write in sandbox
shell command in sandbox
Python execution in sandbox
HTTP/API request through controlled interface
```

Do NOT give unrestricted host access to the agents.

---

# 23. PHASE D — DELEGATION

Implement:

```text
Boss → Manager → Worker
```

The Boss should be able to create child tasks.

Manager should be able to assign work.

Worker executes.

Every delegation should produce task/audit records.

Example:

```text
Main Task
 ├── Manager Task
 │    ├── Worker Task 1
 │    └── Worker Task 2
 └── Manager Task 2
```

Use:

```text
parent_task_id
```

to represent relationships.

---

# 24. PHASE E — REVIEW SUPERVISOR

Create a dedicated reviewer agent role/runtime.

Reviewer should:

1. Understand task requirements.
2. Inspect worker output.
3. Generate appropriate test cases.
4. Execute tests through approved tools.
5. Compare results with requirements.
6. Identify failures.
7. Produce evidence.
8. Store a `task_reviews` record.
9. Return pass/fail.
10. Cause task continuation or completion.

The reviewer should NOT simply output:

```text
"Looks good."
```

It should produce evidence.

Example:

```text
Tests generated: 5
Tests executed: 5
Passed: 5
Failed: 0
Requirement coverage: complete
Security checks: passed
Regression checks: passed

Result: PASS
```

---

# 25. PHASE F — ORCHESTRATION

Create an orchestration loop that can move tasks automatically:

```text
created
 ↓
planned
 ↓
assigned
 ↓
running
 ↓
review
 ↓
running / completed
```

The orchestrator should react to task state rather than requiring the human to manually transition every state.

---

# 26. PHASE G — LOGGING / AUDIT

Every meaningful autonomous action should eventually generate audit records.

Examples:

```text
agent_created
task_created
task_assigned
task_started
tool_requested
governance_checked
tool_executed
output_generated
review_started
review_completed
task_failed
task_completed
```

Keep:

```text
logs
```

separate from:

```text
memory
```

---

# 27. PHASE H — MINIMAL DASHBOARD

Only after the backend autonomous loop works.

Dashboard should initially show:

```text
Tasks
Agents
Hierarchy
Task detail
Agent activity
Review history
Audit history
```

Minimal functionality:

```text
Create task
View status
View delegation
View worker output
View review
View audit
```

Do not spend excessive time on UI polish before the autonomous backend works.

---

# 28. AFTER MVP — ADVANCED AGENT OS

These are NOT prerequisites for the first MVP.

## Memory

Implement:

```text
short-term context
long-term memory
vector retrieval
agent-specific memory
team memory
organizational memory
```

PostgreSQL + pgvector is the intended foundation.

---

## Meetings

Meeting object should contain:

```text
meeting_id
participants
agenda
messages
decisions
action_items
timestamp
```

Agents should be able to call meetings when useful.

---

## MCP Registry

Eventually:

```text
MCP Registry
 ├── MCP server definitions
 ├── tool discovery
 ├── permissions
 ├── health status
 └── versioning
```

---

# 29. CAPABILITY BUILDER

Long-term goal:

If an agent needs something that doesn't exist:

```text
Agent
 ↓
Missing capability detected
 ↓
Capability Builder
 ↓
Generate implementation
 ↓
Static analysis
 ↓
Security checks
 ↓
Sandbox
 ↓
Automated tests
 ↓
Governance evaluation
 ↓
Register capability
 ↓
Version capability
 ↓
Agent uses capability
```

Generated capabilities should be isolated from protected core code.

---

# 30. SELF-IMPROVEMENT

Long-term flow:

```text
Agent proposes improvement
 ↓
Create proposal
 ↓
Generate implementation
 ↓
Run tests
 ↓
Run benchmarks
 ↓
Governance evaluation
 ↓
Version
 ↓
Deploy
 ↓
Monitor
 ↓
Rollback if regression
```

No arbitrary self-modification.

Core governance/identity/audit systems remain protected.

---

# 31. SECURITY REQUIREMENTS

Never allow an LLM to directly bypass:

```text
Governance Engine
Permissions
Audit
Sandbox
Core protection
```

Avoid:

```text
unrestricted shell
unrestricted filesystem
arbitrary network access
direct database destructive access
automatic production deployment
```

Use least authority.

Use explicit permission scopes.

Use sandboxing.

Make dangerous actions auditable.

---

# 32. ESTIMATED MVP DEVELOPMENT SIZE

Current foundation is already substantially implemented.

Remaining first MVP is approximately:

```text
60–90 focused engineering hours
```

A reasonable target is around:

```text
~80 hours
```

This estimate assumes we keep MVP scope disciplined and don't prematurely build the advanced self-improvement/capability-generation system.

---

# 33. IMPORTANT DEVELOPMENT RULES FOR ANTIGRAVITY

Before changing anything:

1. Inspect the current code.
2. Inspect tests.
3. Preserve working behavior.
4. Make small, coherent changes.
5. Run focused tests.
6. Then run the full test suite.
7. Never silently rewrite architecture.
8. Do not introduce unnecessary dependencies.
9. Keep repositories persistence-only.
10. Keep business rules in services.
11. Keep governance centralized.
12. Keep core resources protected.
13. Add tests for every important rule.
14. Prefer migrations over manually changing schema.
15. Do not delete existing test coverage.
16. Do not weaken governance just to make a test pass.

When a file needs major changes, prefer replacing the complete file cleanly rather than performing fragile partial edits.

---

# 34. CURRENT IMMEDIATE COMMANDS

Before continuing development, run:

```bash
python -m pytest
```

Then inspect git:

```bash
git status
```

Do not commit until the current task/review implementation has been verified.

After a coherent milestone passes the full suite:

```bash
git add .
git commit -m "..."
git push
```

---

# 35. FINAL DIRECTION

Do not turn Agent OS into a simple chatbot.

The target architecture is:

```text
                    HUMAN / OWNER
                         │
                         ▼
                       BOSS
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
           MANAGER                MANAGER
              │                     │
         ┌────┴────┐           ┌────┴────┐
         ▼         ▼           ▼         ▼
      TEAM      WORKER       TEAM      WORKER
         │         │           │         │
         └────┬────┘           └────┬────┘
              │                     │
              └──────────┬──────────┘
                         ▼
                    AGENT RUNTIME
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
            MODEL       TOOLS       MEMORY
              │          │          │
              │          ▼          │
              │      GOVERNANCE     │
              │          │          │
              └──────────┼──────────┘
                         ▼
                       AUDIT
                         │
                         ▼
                    AI REVIEWER
                         │
                    PASS / FAIL
                         │
                         ▼
                  COMPLETE / RETRY
```

The defining principle is:

> **Autonomy inside governance.**

Agents should be able to plan, delegate, execute, communicate, create capabilities, and improve workflows autonomously — but every governed action must remain within the Constitution, permissions, security boundaries, resource limits, audit requirements, and rollback requirements.

The immediate priority is NOT advanced self-improvement.

The immediate priority is:

```text
FINISH REVIEW ENFORCEMENT
        ↓
MODEL GATEWAY
        ↓
FIRST AGENT RUNTIME
        ↓
TOOLS
        ↓
DELEGATION
        ↓
AI REVIEWER
        ↓
END-TO-END AUTONOMOUS MVP
```

Build that vertical slice first.
