# TraceForge — Architecture

> **Autonomous AI Incident Investigation & Remediation Platform**
>
> This document defines the technical architecture of TraceForge: its runtime components, boundaries, communication patterns, data flows, agent graph, MCP tool layer, persistence model, security boundaries, deployment topology, and failure-handling strategy.

---

# 1. Architecture Goals

TraceForge is designed around six architectural goals.

### 1.1 Agentic

The system must support:

- Stateful agent workflows
- Multi-agent coordination
- Dynamic task decomposition
- Tool calling
- Parallel investigation
- Long-running tasks
- Human approval
- Recovery from failures

### 1.2 Evidence-driven

Agent conclusions should be grounded in observable evidence.

```text
Claim
 ↓
Evidence IDs
 ↓
Source
 ↓
Raw evidence
```

### 1.3 Controlled autonomy

Agents can investigate autonomously, but actions with meaningful side effects are controlled.

```text
Read → autonomous
Write → permission controlled
High-risk write → human approval
Production mutation → blocked by default
```

### 1.4 Observable

Every important operation should be traceable.

```text
HTTP request
 → investigation
 → agent
 → LLM call
 → tool call
 → database operation
```

### 1.5 Evaluatable

The architecture must make agent behavior measurable and reproducible.

### 1.6 Replaceable

LLM providers, storage implementations, and external integrations should be replaceable without rewriting the agent layer.

---

# 2. High-Level Architecture

```text
                                      ┌───────────────────┐
                                      │       User        │
                                      └─────────┬─────────┘
                                                │
                                                │ HTTPS
                                                ▼
                                      ┌───────────────────┐
                                      │     Next.js       │
                                      │     Frontend      │
                                      └─────────┬─────────┘
                                                │
                                      REST + SSE │
                                                ▼
                                      ┌───────────────────┐
                                      │      FastAPI      │
                                      │     API Layer     │
                                      └───────┬─────┬─────┘
                                              │     │
                               ┌──────────────┘     └──────────────┐
                               │                                   │
                               ▼                                   ▼
                    ┌───────────────────┐               ┌───────────────────┐
                    │    PostgreSQL     │               │       Redis       │
                    │ + pgvector        │               │ Queue / Cache     │
                    └───────────────────┘               └─────────┬─────────┘
                                                                  │
                                                                  ▼
                                                        ┌───────────────────┐
                                                        │  Agent Worker     │
                                                        │                   │
                                                        │   LangGraph       │
                                                        └─────────┬─────────┘
                                                                  │
                                             ┌────────────────────┼────────────────────┐
                                             │                    │                    │
                                             ▼                    ▼                    ▼
                                      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                                      │ Log Agent   │      │ Code Agent  │      │Metrics Agent│
                                      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
                                             │                    │                    │
                                             ▼                    ▼                    ▼
                                      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                                      │  Log MCP    │      │ GitHub MCP  │      │ Metrics MCP │
                                      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
                                             │                    │                    │
                                             ▼                    ▼                    ▼
                                           Logs                 GitHub              Monitoring

                                             ┌───────────────────────────────────────┐
                                             │                                       │
                                             │         Knowledge / RAG Layer         │
                                             │                                       │
                                             └───────────────────┬───────────────────┘
                                                                 │
                                                                 ▼
                                                        Root Cause Agent
                                                                 │
                                                                 ▼
                                                        Remediation Agent
                                                                 │
                                                                 ▼
                                                            Guardrails
                                                                 │
                                                                 ▼
                                                         Human Approval
                                                                 │
                                                                 ▼
                                                         Testing Sandbox
                                                                 │
                                                                 ▼
                                                           GitHub MCP
                                                                 │
                                                                 ▼
                                                            Pull Request
```

---

# 3. System Boundaries

TraceForge is divided into seven major boundaries.

```text
┌───────────────────────────────────────────────────────────────┐
│                         TraceForge                            │
│                                                               │
│  ┌──────────────┐       ┌──────────────┐                     │
│  │ Presentation │ ────> │ Application  │                     │
│  │    Layer     │       │     API      │                     │
│  └──────────────┘       └──────┬───────┘                     │
│                                │                             │
│                         ┌──────▼───────┐                     │
│                         │ Agent Runtime │                     │
│                         └──────┬───────┘                     │
│                                │                             │
│                         ┌──────▼───────┐                     │
│                         │ Tool / MCP    │                     │
│                         │    Layer      │                     │
│                         └──────┬───────┘                     │
│                                │                             │
│                         ┌──────▼───────┐                     │
│                         │ Data / Memory │                     │
│                         └──────────────┘                     │
│                                                               │
│  ┌──────────────┐       ┌──────────────┐                     │
│  │ Evaluation   │       │Observability │                     │
│  └──────────────┘       └──────────────┘                     │
└───────────────────────────────────────────────────────────────┘

             │              │               │
             ▼              ▼               ▼
         GitHub          Logs          Monitoring
```

---

# 4. Component Overview

| Component | Responsibility | Technology |
|---|---|---|
| Web App | User interface | Next.js + TypeScript |
| API | HTTP API and authentication | FastAPI |
| Agent Runtime | Agent orchestration | LangGraph |
| LLM Layer | Model access | Gemini initially |
| MCP Layer | External tool access | MCP |
| Database | Persistent state | PostgreSQL |
| Vector Store | Semantic retrieval | pgvector |
| Queue | Background work | Redis + Celery |
| RAG | Knowledge retrieval | Python + embeddings |
| Guardrails | Safety and policy enforcement | Python |
| Sandbox | Safe code testing | Docker |
| Evaluation | Agent benchmark | Python |
| Observability | Tracing/metrics | OpenTelemetry |
| CI/CD | Build/test/deploy | GitHub Actions |

---

# 5. Frontend Architecture

The frontend is a Next.js application.

```text
frontend/
├── app/
│   ├── dashboard/
│   ├── projects/
│   ├── incidents/
│   ├── investigations/
│   ├── evaluations/
│   ├── agents/
│   └── settings/
│
├── components/
│   ├── incident/
│   ├── investigation/
│   ├── evidence/
│   ├── agents/
│   ├── evaluation/
│   └── common/
│
├── hooks/
├── lib/
├── api/
└── types/
```

---

# 6. Frontend Responsibilities

The frontend should:

- Create projects
- Create incidents
- Start investigations
- Display live investigation events
- Display evidence
- Display root-cause reports
- Display agent activity
- Display remediation plans
- Request human approval
- Display test results
- Display GitHub PRs
- Display evaluation results

The frontend should **not** contain agent orchestration logic.

---

# 7. Frontend → Backend Communication

Primary protocol:

```text
HTTPS
```

REST API:

```text
POST /api/incidents
GET  /api/incidents/{id}
POST /api/incidents/{id}/investigate
```

Live updates:

```text
SSE
```

Example:

```http
GET /api/incidents/INC-1024/events
```

---

# 8. Backend Architecture

FastAPI is the application boundary.

```text
backend/
├── api/
│   ├── routes/
│   │   ├── projects.py
│   │   ├── incidents.py
│   │   ├── investigations.py
│   │   ├── approvals.py
│   │   └── evaluations.py
│   │
│   └── dependencies.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   └── logging.py
│
├── models/
├── schemas/
├── services/
├── repositories/
├── workers/
└── events/
```

---

# 9. Backend Layering

```text
HTTP Request
     │
     ▼
API Route
     │
     ▼
Schema Validation
     │
     ▼
Application Service
     │
     ▼
Repository / Queue
     │
     ▼
Database / Worker
```

Routes should remain thin.

Business logic belongs in services.

Database access belongs in repositories.

---

# 10. Incident Creation Flow

```text
User
 │
 │ POST /api/incidents
 ▼
FastAPI
 │
 ├── Validate request
 │
 ├── Authenticate user
 │
 ├── Authorize project
 │
 └── Create incident
          │
          ▼
      PostgreSQL
          │
          ▼
      Queue job
          │
          ▼
        Redis
```

The API responds quickly:

```json
{
  "incident_id": "INC-1024",
  "status": "QUEUED"
}
```

The actual investigation happens asynchronously.

---

# 11. Worker Architecture

Celery workers execute long-running investigations.

```text
Redis
  │
  ▼
Celery Worker
  │
  ▼
Investigation Runner
  │
  ▼
LangGraph
```

A worker must not trust client input blindly.

It reloads the incident from PostgreSQL using the incident ID.

---

# 12. Agent Runtime

LangGraph is the orchestration layer.

```text
                  START
                    │
                    ▼
              Load Incident
                    │
                    ▼
              Supervisor
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
       Log Agent  Code Agent  Metrics Agent
          │         │         │
          └─────────┼─────────┘
                    ▼
             Knowledge Agent
                    │
                    ▼
             Evidence Merge
                    │
                    ▼
             Root Cause Agent
                    │
             ┌──────┴───────┐
             │              │
        Insufficient       Sufficient
          Evidence          Evidence
             │              │
             ▼              ▼
        More Research    Remediation
             │              │
             └──────┐       │
                    │       ▼
                    │    Guardrails
                    │       │
                    │       ▼
                    │   Human Approval
                    │       │
                    │       ▼
                    │     Patch
                    │       │
                    │       ▼
                    │     Tests
                    │       │
                    │       ▼
                    └──> Complete
```

---

# 13. LangGraph State

The graph operates on a shared typed state.

Conceptually:

```python
class InvestigationState:
    incident_id: str
    project_id: str

    incident: dict

    tasks: list
    completed_tasks: list

    evidence: list
    findings: list
    hypotheses: list

    root_cause: dict | None
    remediation: dict | None

    approval_status: str
    test_results: dict | None

    iteration_count: int
```

State should be persisted/checkpointed so an investigation can recover after worker failure.

---

# 14. Supervisor Responsibilities

The Supervisor is a coordinator, not a universal tool executor.

Input:

```text
Incident
Project context
Existing evidence
Previous investigation state
```

Output:

```text
Investigation plan
Task assignments
Next action
Completion decision
```

Example:

```json
{
  "tasks": [
    {
      "agent": "log_agent",
      "objective": "Find checkout errors"
    },
    {
      "agent": "metrics_agent",
      "objective": "Analyze checkout latency and DB connections"
    },
    {
      "agent": "code_agent",
      "objective": "Inspect recent checkout changes"
    }
  ]
}
```

---

# 15. Parallel Agent Execution

Independent investigation tasks should run concurrently.

```text
                   Supervisor
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    Log Agent      Code Agent     Metrics Agent
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 Evidence Merge
```

This reduces total investigation latency.

The architecture must distinguish:

```text
parallelizable work
```

from:

```text
dependent work
```

For example:

```text
Log analysis
Metrics analysis
Code analysis
```

can run in parallel.

But:

```text
Root cause
```

should wait until sufficient evidence is available.

---

# 16. Evidence Model

Every tool result that may influence a conclusion should become a normalized evidence object.

Conceptually:

```json
{
  "id": "evidence_123",
  "type": "LOG",
  "source": "logging_mcp",
  "service": "checkout-api",
  "timestamp": "...",
  "content": "Database connection pool exhausted",
  "metadata": {},
  "relevance_score": 0.93
}
```

Evidence should be immutable after creation.

---

# 17. Evidence Flow

```text
External System
      │
      ▼
MCP Tool
      │
      ▼
Tool Result
      │
      ▼
Normalizer
      │
      ▼
Evidence Record
      │
      ├──────────> PostgreSQL
      │
      └──────────> Agent State
```

---

# 18. MCP Architecture

MCP is the tool boundary.

```text
                  Agent
                    │
                    ▼
              MCP Client
                    │
           ┌────────┴────────┐
           │                 │
           ▼                 ▼
      MCP Server A      MCP Server B
           │                 │
           ▼                 ▼
        GitHub             Logs
```

MCP servers should expose narrow, typed tools.

---

# 19. GitHub MCP

```text
github_mcp/
├── server.py
├── tools/
│   ├── repository.py
│   ├── code.py
│   ├── commits.py
│   ├── branches.py
│   └── pull_requests.py
└── permissions.py
```

Tools:

```text
get_repository()
search_code()
get_file()
get_recent_commits()
get_commit()
get_diff()
get_pull_request()
create_branch()
commit_changes()
create_pull_request()
```

Read tools can be available to Code Agent.

Write tools require approval.

---

# 20. Logging MCP

```text
logs_mcp/
├── server.py
├── tools/
│   ├── search.py
│   ├── traces.py
│   └── errors.py
└── adapters/
    └── simulator.py
```

Initial implementation:

```text
Synthetic logs
```

Future adapters:

```text
Loki
Elasticsearch
Cloud logging
```

Tools:

```text
search_logs()
get_error_trace()
get_recent_errors()
get_request_logs()
```

---

# 21. Metrics MCP

```text
metrics_mcp/
├── server.py
├── tools/
└── adapters/
    └── simulator.py
```

Tools:

```text
get_metric()
get_metric_history()
get_service_health()
compare_time_windows()
```

Initial backend:

```text
Synthetic metric store
```

---

# 22. Database MCP

Database access should be deliberately restricted.

Allowed initially:

```text
inspect_schema()
describe_table()
run_readonly_query()
get_database_stats()
```

Blocked by default:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
```

A database write should never be available simply because an LLM generated SQL.

---

# 23. Documentation MCP

```text
documentation_mcp/
├── server.py
├── tools/
└── adapters/
```

Tools:

```text
search_documentation()
get_document()
search_runbooks()
get_runbook()
```

The RAG layer can sit behind these tools.

---

# 24. MCP Security Boundary

```text
Agent
  │
  ▼
Tool Request
  │
  ▼
Permission Check
  │
  ├── DENY
  │
  └── ALLOW
       │
       ▼
    Argument Validation
       │
       ▼
    Rate Limit
       │
       ▼
    MCP Server
       │
       ▼
    External System
```

The model must never bypass this boundary.

---

# 25. RAG Architecture

```text
                    Documents
                        │
                        ▼
                  Document Parser
                        │
                        ▼
                    Chunker
                        │
                        ▼
                   Embedding Model
                        │
                        ▼
                  PostgreSQL
                   + pgvector
                        │
                        ▼
                    Retriever
                        │
                        ▼
                 Relevant Chunks
                        │
                        ▼
                     Agent
```

Documents:

```text
Runbooks
Architecture
API documentation
Postmortems
Past incidents
Deployment guides
Database documentation
```

---

# 26. Retrieval Metadata

Every chunk should contain metadata.

```json
{
  "document_id": "doc_123",
  "chunk_id": "chunk_42",
  "type": "RUNBOOK",
  "service": "checkout-api",
  "version": "v2",
  "source": "checkout.md"
}
```

This allows filtered retrieval.

Example:

```text
service = checkout-api
type = RUNBOOK
```

---

# 27. Retrieval Pipeline

The initial retrieval pipeline:

```text
Query
 ↓
Embedding
 ↓
Vector Search
 ↓
Top K
 ↓
Metadata Filtering
 ↓
Optional Reranking
 ↓
Context
 ↓
Agent
```

Do not send the entire knowledge base to the LLM.

---

# 28. Memory Architecture

TraceForge separates working state from persistent memory.

```text
                  Agent
                    │
            ┌───────┴────────┐
            │                │
            ▼                ▼
      Working State     Persistent Memory
            │                │
       LangGraph         PostgreSQL
            │                │
            │             pgvector
            │                │
            └────────┬───────┘
                     ▼
                 Future Runs
```

---

# 29. LLM Provider Layer

The agent layer should not directly instantiate a specific provider everywhere.

Instead:

```text
Agent
 │
 ▼
LLM Gateway
 │
 ├── Gemini
 ├── OpenAI
 ├── Anthropic
 └── Local Model
```

Example interface:

```python
class LLMProvider:
    async def generate(...)
    async def structured_output(...)
    async def tool_call(...)
```

The first implementation uses Gemini.

---

# 30. Structured Outputs

Important agent outputs should use schemas.

Example:

```python
class RootCauseReport(BaseModel):
    root_cause: str
    confidence: float
    evidence_ids: list[str]
    alternative_hypotheses: list[str]
    uncertainty: list[str]
```

The system validates model output before it enters application state.

---

# 31. Guardrail Architecture

Guardrails sit between the agent and sensitive actions.

```text
Agent
 │
 ▼
Intent
 │
 ▼
Tool Authorization
 │
 ▼
Argument Validation
 │
 ▼
Risk Classification
 │
 ├── LOW → Execute
 │
 ├── MEDIUM → Approval
 │
 └── HIGH → Block / Approval
```

---

# 32. Risk Levels

### LOW

```text
Read logs
Read metrics
Search code
Read documentation
```

### MEDIUM

```text
Create branch
Generate patch
Create PR
```

### HIGH

```text
Database mutation
Production deployment
Infrastructure modification
Secret access
```

High-risk actions should be blocked by default in the public demo.

---

# 33. Human Approval Flow

```text
Remediation Agent
       │
       ▼
Proposed Action
       │
       ▼
Risk Classifier
       │
       ▼
Approval Required
       │
       ▼
Frontend
       │
   ┌───┴────┐
   ▼        ▼
Approve   Reject
   │        │
   ▼        ▼
Execute   Stop
```

Approval must be explicit.

---

# 34. Remediation Architecture

```text
Root Cause
    │
    ▼
Remediation Agent
    │
    ├── affected files
    ├── proposed change
    ├── expected impact
    ├── risk
    └── validation plan
          │
          ▼
     Human Approval
          │
          ▼
       Patch
          │
          ▼
      Sandbox
```

---

# 35. Sandbox Architecture

Generated code runs in an isolated environment.

```text
                    Patch
                      │
                      ▼
              Sandbox Manager
                      │
                      ▼
               Docker Container
                      │
          ┌───────────┼───────────┐
          │           │           │
       Build       Unit Tests   Integration
          │           │           │
          └───────────┼───────────┘
                      ▼
                 Test Report
```

Sandbox restrictions:

```text
CPU limit
Memory limit
Execution timeout
Restricted network
Temporary filesystem
No production secrets
```

---

# 36. Testing Agent

The Testing Agent consumes:

```text
Repository
+
Patch
+
Test configuration
```

It returns:

```json
{
  "status": "PASS",
  "tests_total": 169,
  "tests_passed": 169,
  "tests_failed": 0,
  "duration_seconds": 18.4
}
```

If failures occur:

```text
Testing Agent
    ↓
Failure Evidence
    ↓
Remediation Agent
    ↓
New Patch
```

Maximum repair iterations must be enforced.

---

# 37. GitHub Pull Request Flow

```text
Approved Patch
      │
      ▼
GitHub MCP
      │
      ├── create_branch()
      │
      ├── commit_changes()
      │
      └── create_pull_request()
                    │
                    ▼
                GitHub PR
```

The PR should contain:

```text
Problem
Root Cause
Evidence
Changes
Tests
Risk
Agent-generated summary
```

---

# 38. Database Architecture

PostgreSQL is the system of record.

Primary tables:

```text
users
projects
project_connections

incidents
investigations
agent_runs
tool_calls

evidence
hypotheses
root_causes
remediation_plans

approvals
test_runs

documents
document_chunks

evaluation_runs
evaluation_cases
evaluation_results

audit_logs
```

---

# 39. Database Ownership

```text
API
 │
 ▼
Application Services
 │
 ▼
Repositories
 │
 ▼
PostgreSQL
```

Agents should not directly manipulate database tables.

They should use application services or approved MCP tools.

---

# 40. Redis Architecture

Redis has three primary roles.

## Queue

```text
FastAPI
 ↓
Redis
 ↓
Celery
```

## Cache

Examples:

```text
frequently retrieved project configuration
temporary retrieval results
short-lived metadata
```

## Coordination

Possible uses:

```text
distributed locks
investigation ownership
rate limiting
```

Persistent business state must remain in PostgreSQL.

---

# 41. Event Architecture

Investigation events are generated by the backend.

Example:

```json
{
  "type": "agent.completed",
  "incident_id": "INC-1024",
  "agent": "log_agent",
  "timestamp": "...",
  "metadata": {
    "evidence_count": 12
  }
}
```

Event flow:

```text
Agent
 ↓
Event Publisher
 ↓
Redis / Event Bus
 ↓
SSE Connection
 ↓
Next.js
```

For the initial implementation, a simpler database-backed event stream may be used before introducing a dedicated event bus.

---

# 42. API Architecture

```text
/api
├── /auth
├── /projects
├── /incidents
├── /investigations
├── /evidence
├── /approvals
├── /remediation
├── /evaluations
└── /health
```

The API should expose application capabilities, not raw agent internals.

---

# 43. Core API Flow

### Create Incident

```http
POST /api/incidents
```

### Start Investigation

```http
POST /api/incidents/{id}/investigate
```

### Stream Investigation

```http
GET /api/incidents/{id}/events
```

### Get Evidence

```http
GET /api/incidents/{id}/evidence
```

### Get Report

```http
GET /api/incidents/{id}/report
```

### Approve

```http
POST /api/incidents/{id}/approval
```

---

# 44. Authentication Boundary

```text
Browser
   │
   ▼
Authentication
   │
   ▼
Identity
   │
   ▼
Project Authorization
   │
   ▼
API
```

Every project-scoped resource must be authorized against the authenticated user.

---

# 45. RBAC

Initial roles:

```text
VIEWER
ENGINEER
ADMIN
```

Example:

| Action | Viewer | Engineer | Admin |
|---|---:|---:|---:|
| View incident | ✓ | ✓ | ✓ |
| Start investigation | ✓ | ✓ | ✓ |
| View evidence | ✓ | ✓ | ✓ |
| Approve remediation | — | ✓ | ✓ |
| Configure tools | — | — | ✓ |
| Manage users | — | — | ✓ |

---

# 46. Observability Architecture

Use OpenTelemetry instrumentation.

```text
Frontend
   │
   ▼
FastAPI
   │
   ▼
Investigation
   │
   ├── Agent
   │    └── LLM
   │
   ├── MCP
   │    └── External API
   │
   └── Database
```

Each operation should propagate:

```text
trace_id
span_id
incident_id
investigation_id
```

---

# 47. Trace Example

```text
TRACE: trace_123

FastAPI POST /investigate
│
├── Queue Investigation
│
└── Worker
    │
    └── LangGraph
        │
        ├── Supervisor
        │
        ├── Log Agent
        │   └── search_logs
        │
        ├── Metrics Agent
        │   └── get_metric_history
        │
        ├── Code Agent
        │   ├── get_recent_commits
        │   └── get_diff
        │
        └── Root Cause Agent
```

---

# 48. Logging

Use structured JSON logs.

Example:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "agent-worker",
  "event": "tool_completed",
  "incident_id": "INC-1024",
  "agent": "log_agent",
  "tool": "search_logs",
  "duration_ms": 842
}
```

Never log:

```text
API keys
OAuth tokens
Passwords
Database credentials
Private secrets
```

---

# 49. Evaluation Architecture

Evaluation runs independently from production investigations.

```text
Evaluation Dataset
        │
        ▼
Scenario Runner
        │
        ▼
TraceForge
        │
        ▼
Evaluation Collectors
        │
        ├── Root Cause Evaluator
        ├── Evidence Evaluator
        ├── Tool Evaluator
        ├── Safety Evaluator
        └── Completion Evaluator
        │
        ▼
Evaluation Database
        │
        ▼
Evaluation Dashboard
```

---

# 50. Evaluation Dataset

Each test case contains:

```json
{
  "id": "incident_001",
  "title": "...",
  "description": "...",
  "service": "checkout-api",

  "ground_truth": {
    "root_cause": "...",
    "required_evidence": [],
    "expected_tools": [],
    "expected_remediation": "..."
  }
}
```

---

# 51. Evaluation Isolation

Evaluation should run against a controlled environment.

```text
Evaluation
    │
    ▼
Demo Infrastructure
    │
    ├── Synthetic Logs
    ├── Synthetic Metrics
    ├── Git Repository
    └── Documents
```

This provides deterministic ground truth.

---

# 52. Failure Architecture

TraceForge assumes components can fail.

Potential failures:

```text
LLM timeout
LLM malformed output
MCP timeout
GitHub rate limit
Database failure
Redis failure
Worker crash
Sandbox timeout
Agent loop
Insufficient evidence
Conflicting evidence
```

---

# 53. Failure Handling Strategy

```text
Operation
   │
   ▼
Execute
   │
   ├── Success → Continue
   │
   └── Failure
         │
         ▼
       Retry?
         │
      ┌──┴───┐
     YES     NO
      │       │
      ▼       ▼
  Backoff   Fallback
              │
              ▼
        Human Escalation
```

Retries must be bounded.

---

# 54. Agent Loop Protection

Each investigation receives budgets:

```text
MAX_ITERATIONS
MAX_TOOL_CALLS
MAX_DURATION
MAX_LLM_CALLS
MAX_TOKEN_BUDGET
```

If any budget is exceeded:

```text
INVESTIGATION
      ↓
BUDGET_EXCEEDED
      ↓
HUMAN_REVIEW
```

---

# 55. Deployment Architecture — Initial

For the first deployed version:

```text
                       Internet
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
             Vercel                Backend
             Next.js               FastAPI
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
               PostgreSQL           Redis           Worker
               + pgvector                             │
                                                     │
                                                     ▼
                                                  LangGraph
```

This keeps initial infrastructure manageable.

---

# 56. Deployment Architecture — Scaled

A later architecture can move toward:

```text
                         Internet
                            │
                            ▼
                       CloudFront
                            │
                            ▼
                      Load Balancer
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
             API Service         Frontend
                  │
          ┌───────┴────────┐
          │                │
          ▼                ▼
      Redis Queue       PostgreSQL
          │             + pgvector
          ▼
     Agent Workers
          │
          ├── LangGraph
          ├── MCP
          └── Sandbox
```

Potential AWS mapping:

```text
CloudFront
ALB
ECS/Fargate
RDS PostgreSQL
ElastiCache Redis
S3
CloudWatch
Secrets Manager
```

The AWS architecture is optional for the first release.

---

# 57. CI/CD Architecture

```text
Developer
   │
   ▼
Git Push
   │
   ▼
GitHub Actions
   │
   ├── Lint
   ├── Type Check
   ├── Unit Tests
   ├── Integration Tests
   ├── Agent Tests
   ├── Evaluation Benchmark
   │
   └── Build
        │
        ▼
      Docker
        │
        ▼
      Deploy
```

---

# 58. AI Regression Gate

The CI pipeline should optionally evaluate agent performance.

```text
Code Change
     ↓
Tests
     ↓
Agent Benchmark
     ↓
Compare Against Baseline
     │
     ├── Pass → Deploy
     │
     └── Regression → Block
```

Example:

```text
Baseline Root Cause Accuracy: 87%

New Version: 78%

Threshold: 85%

Deployment: BLOCKED
```

---

# 59. Security Architecture

Security boundaries:

```text
User
 │
 ▼
Auth
 │
 ▼
API Authorization
 │
 ▼
Agent Runtime
 │
 ▼
Tool Authorization
 │
 ▼
MCP
 │
 ▼
External System
```

Sensitive operations require multiple checks.

---

# 60. Secret Management

Secrets should be stored outside application source code.

Development:

```text
.env
```

Production:

```text
Cloud Secrets Manager
```

Agents should receive only the minimum credentials necessary for the requested tool.

---

# 61. Principle of Least Privilege

Example:

The Log Agent should receive:

```text
logs:read
```

It should not receive:

```text
github:write
database:write
deployment:write
```

The Code Agent may receive:

```text
github:read
```

A remediation workflow may temporarily request:

```text
github:write
```

only after approval.

---

# 62. Network Security

The sandbox should not have unrestricted outbound network access.

MCP servers should have controlled connectivity to their respective systems.

```text
Agent Worker
    │
    ├── MCP GitHub → GitHub
    ├── MCP Logs → Log Store
    └── MCP Metrics → Metrics Store
```

Avoid giving the worker unrestricted internet access merely because one tool requires external access.

---

# 63. Data Flow — Complete Investigation

```text
USER
 │
 │ incident
 ▼
NEXT.JS
 │
 │ POST /api/incidents
 ▼
FASTAPI
 │
 ├── PostgreSQL: create incident
 │
 └── Redis: queue investigation
          │
          ▼
       CELERY
          │
          ▼
     LANGGRAPH
          │
          ▼
     SUPERVISOR
          │
   ┌──────┼────────┐
   │      │        │
   ▼      ▼        ▼
 LOG    CODE     METRICS
AGENT   AGENT     AGENT
   │      │        │
   ▼      ▼        ▼
 MCP    MCP       MCP
   │      │        │
   ▼      ▼        ▼
 LOGS   GITHUB   METRICS
   │      │        │
   └──────┼────────┘
          ▼
      EVIDENCE
          │
          ▼
       RAG/MEMORY
          │
          ▼
    ROOT CAUSE AGENT
          │
          ▼
    REMEDIATION AGENT
          │
          ▼
       GUARDRAILS
          │
          ▼
    HUMAN APPROVAL
          │
          ▼
       SANDBOX
          │
          ▼
       TESTING
          │
          ▼
      GITHUB MCP
          │
          ▼
       GITHUB PR
          │
          ▼
        USER
```

---

# 64. Complete Data Lifecycle

## Incident

```text
Created
 ↓
Queued
 ↓
Investigating
 ↓
Resolved
```

## Evidence

```text
Retrieved
 ↓
Normalized
 ↓
Stored
 ↓
Referenced
 ↓
Included in report
```

## Remediation

```text
Proposed
 ↓
Approved
 ↓
Generated
 ↓
Tested
 ↓
PR Created
```

---

# 65. Concurrency Model

TraceForge has multiple concurrency levels.

### Request concurrency

FastAPI handles multiple users.

### Job concurrency

Celery processes multiple investigations.

### Agent concurrency

Independent agents investigate in parallel.

### Tool concurrency

Independent tool calls may run concurrently.

The system must still enforce:

```text
per-user limits
per-project limits
per-agent limits
provider rate limits
resource limits
```

---

# 66. Idempotency

Operations that may be retried should be idempotent.

Examples:

```text
Create incident
Create branch
Create PR
Start investigation
```

Use idempotency keys where appropriate.

Example:

```http
Idempotency-Key: investigation-INC-1024-v1
```

This prevents duplicate actions after retries.

---

# 67. State Consistency

PostgreSQL is the source of truth for business state.

Redis is not the source of truth.

Agent memory should not be the only copy of important information.

Example:

```text
Agent decides root cause
       ↓
Persist RootCause record
       ↓
Update LangGraph state
       ↓
Publish event
```

---

# 68. Eventual Consistency

Some UI data may be eventually consistent.

For example:

```text
Agent completes
 ↓
Database updated
 ↓
Event published
 ↓
Frontend receives event
```

The UI should tolerate events arriving slightly after the underlying database update.

---

# 69. Caching Strategy

Cache only data where stale values are acceptable.

Good candidates:

```text
project metadata
documentation retrieval
static configuration
```

Avoid caching:

```text
approval state
security permissions
current incident status
write operation state
```

unless carefully invalidated.

---

# 70. Performance Strategy

Primary performance goals:

```text
Fast incident creation
Parallel investigation
Streaming progress
Bounded agent execution
Efficient retrieval
```

Do not optimize LLM latency prematurely.

First measure.

---

# 71. Cost Control

The architecture should track:

```text
LLM calls
Input tokens
Output tokens
Embedding calls
Tool calls
Investigation duration
```

Potential controls:

```text
Model selection
Caching
Context limits
Agent budgets
Parallelism
Retrieval top-K limits
```

---

# 72. Observability for Cost

Each LLM invocation should record:

```text
provider
model
input_tokens
output_tokens
latency
estimated_cost
incident_id
agent
```

This allows:

```text
Cost / investigation
Cost / successful resolution
Cost / agent
```

---

# 73. Testing Architecture

Testing layers:

```text
Unit
 │
 ├── Tools
 ├── Services
 ├── Guardrails
 └── Parsers

Integration
 │
 ├── Database
 ├── Redis
 ├── MCP
 └── RAG

Agent
 │
 ├── Supervisor
 ├── Individual agents
 └── Graph transitions

End-to-End
 │
 └── Full incident workflow

Evaluation
 │
 └── Benchmark scenarios
```

---

# 74. Deterministic Simulator

The simulator is critical for reproducibility.

Each scenario should define:

```text
service state
logs
metrics
repository state
documentation
failure injection
ground truth
```

Example:

```text
Scenario:
checkout-db-pool-exhaustion

Cause:
Transaction holds connection during payment API call

Expected evidence:
db_connections
checkout timeout logs
recent transaction commit
checkout runbook

Expected remediation:
Move payment call outside transaction
```

---

# 75. Simulator Architecture

```text
simulator/
├── scenarios/
│   ├── db_pool_exhaustion/
│   ├── redis_failure/
│   ├── payment_timeout/
│   └── memory_leak/
│
├── services/
├── logs/
├── metrics/
├── repository/
└── loader.py
```

The simulator should be resettable between evaluations.

---

# 76. Demo Mode Architecture

A recruiter should be able to use:

```text
Demo Mode
```

without:

```text
GitHub credentials
AWS credentials
Monitoring credentials
Database credentials
```

The demo environment uses safe local/synthetic integrations.

---

# 77. Production Mode Architecture

Production mode can later support:

```text
GitHub OAuth/App
Monitoring API
Log API
Database connection
Documentation sources
```

Production credentials are encrypted and scoped.

---

# 78. Multi-Tenancy Direction

The architecture should eventually support:

```text
Organization
 ├── Users
 ├── Projects
 │    ├── Connections
 │    ├── Incidents
 │    └── Knowledge
```

Every database record that belongs to a customer should be scoped to the organization/project.

---

# 79. Extensibility

New agents should be addable without changing the core graph excessively.

Example future agents:

```text
Security Agent
Cost Agent
Cloud Agent
Database Agent
Dependency Agent
Performance Agent
```

New tools should be addable through MCP.

---

# 80. Example Future Investigation

A more advanced investigation might become:

```text
Incident
   ↓
Supervisor
   ↓
┌──────────┬──────────┬──────────┬──────────┐
│ Logs     │ Metrics  │ Code     │ Security │
└──────────┴──────────┴──────────┴──────────┘
                ↓
          Evidence Graph
                ↓
        Hypothesis Generation
                ↓
        Hypothesis Testing
                ↓
           Root Cause
                ↓
       Remediation Planning
                ↓
          Risk Assessment
                ↓
        Human Approval
                ↓
          Sandbox Test
                ↓
              PR
```

---

# 81. Evidence Graph

A future improvement is to model relationships explicitly.

```text
Incident
   │
   ├── affects → checkout-api
   │
   ├── produced → error_log_123
   │
   ├── correlated_with → metric_42
   │
   ├── changed_by → commit_8a92bc
   │
   └── explained_by → runbook_14
```

This can make evidence correlation more structured than passing large text blobs between agents.

---

# 82. Architecture Trade-offs

## PostgreSQL + pgvector vs dedicated vector database

### Initial choice

PostgreSQL + pgvector.

Reason:

- Fewer moving parts
- Relational + semantic data together
- Easier deployment
- Sufficient for project scale

A dedicated vector database can be evaluated later.

---

## Celery vs direct background tasks

### Initial choice

Celery + Redis.

Reason:

- Explicit worker architecture
- Retries
- Long-running tasks
- Scalable worker model

A simpler queue may be used during the earliest prototype.

---

## SSE vs WebSockets

### Initial choice

SSE.

Reason:

- Primarily server → client updates
- Simpler than bidirectional WebSockets
- Appropriate for investigation timelines

WebSockets can be introduced if interactive bidirectional control becomes necessary.

---

# 83. Failure Isolation

One failing agent should not necessarily terminate the entire investigation.

Example:

```text
Log Agent       ✓
Metrics Agent   ✓
Code Agent      ✗
Knowledge Agent ✓
```

Supervisor may continue:

```text
Code Agent unavailable.

Proceed using:
Logs
Metrics
Knowledge
Historical incidents
```

The final report must disclose missing evidence.

---

# 84. Partial Results

Long investigations should persist partial results.

Example:

```text
Investigation
 ├── Log Agent ✓
 ├── Metrics Agent ✓
 ├── Code Agent pending
 └── Knowledge Agent ✓
```

If the worker crashes, the investigation can resume instead of restarting from zero.

---

# 85. Checkpointing

LangGraph checkpoints should persist important workflow state.

```text
Checkpoint 1
 └── Investigation planned

Checkpoint 2
 └── Logs collected

Checkpoint 3
 └── Metrics collected

Checkpoint 4
 └── Root cause identified
```

A worker can resume from the latest valid checkpoint.

---

# 86. Production Safety Rule

The system must maintain a strict separation between:

```text
INVESTIGATION
```

and:

```text
EXECUTION
```

Investigation may be autonomous.

Execution is controlled.

```text
AI:
"I think this is the problem."

Human:
"Show me the evidence."

AI:
"Here is the evidence."

Human:
"Show me the fix."

AI:
"Here is the proposed patch and tests."

Human:
"Approve."

AI:
"Create PR."
```

This is the intended autonomy model.

---

# 87. Final Architecture

```text
                              USER
                               │
                               ▼
                         NEXT.JS WEB APP
                               │
                         HTTPS + SSE
                               │
                               ▼
                           FASTAPI
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
           PostgreSQL        Redis          Auth
           + pgvector        Queue
                │              │
                │              ▼
                │          Celery Worker
                │              │
                │              ▼
                │          LANGGRAPH
                │              │
                │         SUPERVISOR
                │              │
                │      ┌───────┼────────┐
                │      │       │        │
                │      ▼       ▼        ▼
                │     LOG     CODE    METRICS
                │    AGENT    AGENT    AGENT
                │      │       │        │
                │      ▼       ▼        ▼
                │     MCP     MCP      MCP
                │      │       │        │
                │      ▼       ▼        ▼
                │    LOGS    GITHUB   METRICS
                │      │       │        │
                └──────┴───────┼────────┘
                               ▼
                         KNOWLEDGE/RAG
                               │
                         MEMORY/PGVECTOR
                               │
                               ▼
                       ROOT CAUSE AGENT
                               │
                               ▼
                       REMEDIATION AGENT
                               │
                               ▼
                          GUARDRAILS
                               │
                               ▼
                       HUMAN APPROVAL
                               │
                               ▼
                         TEST SANDBOX
                               │
                               ▼
                          GITHUB MCP
                               │
                               ▼
                         GITHUB PR


       ┌───────────────────────────────────────────────┐
       │               CROSS-CUTTING                   │
       │                                               │
       │  OpenTelemetry │ Evaluation │ Security       │
       │  Audit Logs    │ CI/CD      │ Rate Limits    │
       │  Cost Tracking │ Testing    │ Secret Mgmt    │
       └───────────────────────────────────────────────┘
```

---

# 88. Architecture In One Sentence

> **TraceForge is a stateful, observable, evaluation-driven multi-agent runtime that uses LangGraph for orchestration, MCP for controlled tool access, PostgreSQL/pgvector for persistence and knowledge retrieval, Redis/Celery for asynchronous execution, guardrails and human approval for safe actions, and a sandbox for validating AI-generated remediation before creating a GitHub pull request.**

---

# 89. Implementation Order

The architecture should be implemented in this order:

```text
01. Project skeleton
02. PostgreSQL
03. FastAPI
04. Incident API
05. Demo simulator
06. Single Log Agent
07. LangGraph state
08. Supervisor
09. Metrics Agent
10. Code Agent
11. Evidence normalization
12. Root Cause Agent
13. Next.js dashboard
14. SSE investigation timeline
15. RAG
16. Memory
17. MCP servers
18. Redis
19. Celery
20. Remediation Agent
21. Sandbox
22. Human approval
23. Guardrails
24. Evaluation framework
25. OpenTelemetry
26. Authentication/RBAC
27. Docker
28. CI/CD
29. Cloud deployment
30. Benchmark + optimization
```

Do not implement all 30 steps simultaneously.

Each step should leave the system runnable.

---

# 90. Architectural Definition of Done

The architecture is successfully implemented when:

```text
✓ User can create an incident
✓ Incident is persisted
✓ Investigation runs asynchronously
✓ LangGraph coordinates agents
✓ Agents share structured state
✓ Agents can call MCP tools
✓ MCP tools access controlled data sources
✓ Evidence is persisted
✓ RAG retrieves relevant knowledge
✓ Historical incidents can be retrieved
✓ Root cause references evidence
✓ Remediation can be generated
✓ High-risk actions require approval
✓ Code can be tested in a sandbox
✓ GitHub PR can be created after approval
✓ Investigation progress streams to frontend
✓ Agent execution is observable
✓ Agent performance is evaluated
✓ Failed operations recover safely
✓ Investigation can resume from checkpoints
✓ Demo scenarios are reproducible
✓ The system can be deployed
```

---

# 91. Architectural North Star

TraceForge should evolve from:

```text
Simple AI Agent
```

into:

```text
              AI ENGINEERING SYSTEM

                    ┌──────────┐
                    │   LLM    │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Agents  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
           Tools       Memory      RAG
              │          │          │
              └──────────┼──────────┘
                         │
                   Orchestration
                         │
                    Guardrails
                         │
                   Evaluation
                         │
                  Observability
                         │
                  Infrastructure
                         │
                    Production
```

The goal is not to maximize the number of technologies.

The goal is to demonstrate that every architectural component solves a real problem in an agentic AI system.
