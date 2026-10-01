# TraceForge — System Design

> **Autonomous AI Incident Investigation & Remediation Platform**
>
> TraceForge is an agentic AI platform that investigates software incidents using logs, metrics, source code, documentation, incident history, and other engineering tools. It correlates evidence, identifies probable root causes, proposes remediation, validates fixes in a sandbox, and—only with explicit human approval—creates a GitHub pull request.

---

## 1. Product Vision

TraceForge is designed to answer:

> **"My production system is broken. Can an AI engineer investigate it, explain why it broke, and help prepare the fix?"**

Traditional monitoring systems tell engineers that something is wrong.

Traditional observability platforms expose logs and metrics.

TraceForge sits above those systems as an **AI investigation and remediation layer**.

It does not replace observability infrastructure. It consumes evidence from those systems and reasons over it.

### Core loop

```text
Incident
   ↓
Investigate
   ↓
Collect Evidence
   ↓
Correlate Evidence
   ↓
Generate Hypotheses
   ↓
Test Hypotheses
   ↓
Identify Root Cause
   ↓
Plan Remediation
   ↓
Human Approval
   ↓
Sandbox Validation
   ↓
Pull Request
```

---

# 2. Problem Statement

When a production incident occurs, an engineer may need to inspect:

- Application logs
- Error traces
- Metrics
- Recent Git commits
- Pull requests
- Database state
- Infrastructure state
- Architecture documentation
- Runbooks
- Previous incidents
- Postmortems

The information is distributed across multiple systems.

The engineer must manually correlate these sources.

TraceForge attempts to automate the investigation while keeping:

- Evidence visible
- Actions controlled
- Dangerous operations gated
- Agent behavior observable
- Results measurable

---

# 3. Target Users

## Primary User — Software Engineer / SRE

A developer or SRE receives an incident and wants to understand:

- What happened?
- Which service is affected?
- What changed recently?
- What evidence supports the diagnosis?
- What is the likely root cause?
- What should be changed?
- Is the proposed fix safe?
- Can the fix be tested automatically?

## Secondary User — Engineering Manager

Wants:

- Incident history
- Investigation reports
- Root-cause trends
- AI performance metrics
- Mean investigation time
- Evaluation results

## Demo User — Recruiter / Interviewer

The system must allow someone unfamiliar with the project to experience a complete investigation without connecting their own infrastructure.

Therefore TraceForge provides a **Demo Environment** with predefined applications and incidents.

---

# 4. Product Experience

## 4.1 Project Setup

The user creates or selects a project.

### Production mode

The user can connect:

```text
GitHub Repository
Monitoring Provider
Log Provider
Database
Documentation
```

### Demo mode

The system provides:

```text
Demo E-commerce Application
├── GitHub repository
├── Synthetic logs
├── Synthetic metrics
├── PostgreSQL database
├── Runbooks
├── Architecture documents
└── Historical incidents
```

The demo environment is the primary path for public demonstrations.

---

# 5. Creating an Incident

The user creates an incident:

```text
Title:
Checkout API returning HTTP 500 errors

Description:
Customers are unable to complete checkout.
Errors started approximately 10 minutes ago.

Severity:
HIGH

Service:
checkout-api
```

The frontend sends:

```http
POST /api/incidents
```

Example:

```json
{
  "title": "Checkout API returning HTTP 500 errors",
  "description": "Customers are unable to complete checkout.",
  "severity": "HIGH",
  "service": "checkout-api",
  "project_id": "project_123"
}
```

The backend creates an incident and starts an asynchronous investigation.

---

# 6. User Experience During Investigation

The user sees a live investigation timeline.

Example:

```text
INCIDENT #1024
Checkout API returning HTTP 500 errors

Status: INVESTIGATING

Agent Activity

✓ Supervisor
  Created investigation plan

✓ Log Agent
  Retrieved 1,204 relevant logs

✓ Metrics Agent
  Analyzed 6 metrics

✓ Code Agent
  Analyzed 7 recent commits

✓ Knowledge Agent
  Retrieved 3 relevant documents

● Root Cause Agent
  Correlating evidence...
```

The UI must expose progress without exposing private chain-of-thought.

The system should show:

- Actions taken
- Tools used
- Evidence retrieved
- Findings
- Confidence
- Errors/retries
- Final conclusions

It should not expose hidden reasoning or private model chain-of-thought.

---

# 7. Final Investigation Report

Example:

```text
ROOT CAUSE
──────────────────────────────

Checkout transaction scope regression

Confidence: 91%

Summary:
A recent change caused database connections to remain
occupied while waiting for an external payment API.

Evidence:

[LOG]
Database connection pool exhausted.

[METRIC]
98 / 100 database connections.

[GITHUB]
Recent commit changed checkout transaction handling.

[RUNBOOK]
External payment calls must not occur inside
database transactions.
```

The report must distinguish:

### Facts

Directly observed data.

### Inferences

Conclusions derived from evidence.

### Uncertainty

Areas where evidence is insufficient.

---

# 8. Core Architecture

```text
                         ┌────────────────────┐
                         │       User         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      Next.js       │
                         │     Frontend       │
                         └─────────┬──────────┘
                                   │
                              HTTP / SSE
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      FastAPI       │
                         │      Backend       │
                         └─────────┬──────────┘
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                         ▼                   ▼
                    PostgreSQL             Redis
                         │                   │
                         │              Job Queue
                         │                   │
                         └─────────┬─────────┘
                                   ▼
                         ┌────────────────────┐
                         │    Agent Worker    │
                         │                    │
                         │    LangGraph       │
                         └─────────┬──────────┘
                                   │
             ┌─────────────────────┼──────────────────────┐
             │                     │                      │
             ▼                     ▼                      ▼
        Log Agent             Code Agent            Metrics Agent
             │                     │                      │
             ▼                     ▼                      ▼
        Log MCP               GitHub MCP              Metrics MCP
             │                     │                      │
             ▼                     ▼                      ▼
          Logs                  GitHub                Monitoring
             │                     │                      │
             └─────────────────────┼──────────────────────┘
                                   ▼
                         Evidence Aggregation
                                   │
                                   ▼
                         Knowledge / RAG
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

# 9. Architectural Principles

## 9.1 Evidence First

Agents should not make high-confidence claims without supporting evidence.

Every important conclusion should reference evidence IDs.

---

## 9.2 Read Before Write

Agents may freely perform approved read-only investigation operations.

Write operations require stronger controls.

```text
READ
✓ Logs
✓ Metrics
✓ Source code
✓ Documentation
✓ Incident history

WRITE
⚠ Modify source code
⚠ Create branch
⚠ Commit
⚠ Create PR
⚠ Database mutation
⚠ Deployment
```

---

## 9.3 Human-in-the-Loop

High-risk actions require explicit approval.

TraceForge should never autonomously deploy changes to production.

---

## 9.4 Tool Isolation

Agents should interact with external systems through controlled tools.

Agents should not receive unrestricted network access or arbitrary shell execution.

---

## 9.5 Provider Independence

LLM providers should be abstracted behind a provider interface.

Initial provider:

```text
Gemini
```

Future providers:

```text
OpenAI
Anthropic
Local Models
```

---

## 9.6 Observable Agents

Every agent execution should produce structured telemetry:

```text
agent
run_id
incident_id
start_time
end_time
status
model
tokens
tools_called
errors
latency
```

---

# 10. Agent Architecture

## 10.1 Supervisor Agent

### Responsibility

The Supervisor is responsible for coordinating the investigation.

It should:

- Understand the incident
- Determine investigation tasks
- Delegate tasks
- Track state
- Detect missing evidence
- Resolve conflicts
- Decide when investigation is complete

It should not directly perform every investigation operation.

### Example

```text
Incident:
Checkout API returns 500

Supervisor:

1. Inspect application logs
2. Inspect service metrics
3. Inspect recent code changes
4. Search relevant runbooks
5. Correlate evidence
6. Determine root cause
```

---

# 11. Log Agent

### Responsibility

Investigate application and infrastructure logs.

### Example tools

```text
search_logs()
get_error_trace()
get_recent_errors()
get_request_logs()
```

### Example

```python
search_logs(
    service="checkout-api",
    query="500",
    start_time="...",
    end_time="..."
)
```

### Output

```json
{
  "finding": "Database connection pool exhausted",
  "evidence_ids": ["log_123", "log_127"],
  "confidence": 0.88
}
```

---

# 12. Metrics Agent

### Responsibility

Analyze time-series metrics.

### Example tools

```text
get_metric()
get_metric_history()
get_service_health()
compare_time_windows()
```

### Example

```python
get_metric(
    name="db_connections",
    service="checkout-api",
    range="last_30_minutes"
)
```

### Output

```json
{
  "metric": "db_connections",
  "current": 98,
  "baseline": 42,
  "maximum": 100,
  "finding": "Connection utilization is abnormally high."
}
```

---

# 13. Code Agent

### Responsibility

Investigate the source repository.

### Example tools

```text
search_code()
get_file()
get_commit()
get_diff()
get_recent_commits()
get_pull_requests()
```

### Example workflow

```text
Recent incident
    ↓
Find affected service
    ↓
Inspect recent commits
    ↓
Inspect relevant files
    ↓
Inspect commit diff
    ↓
Identify suspicious change
```

---

# 14. Knowledge Agent

### Responsibility

Retrieve relevant engineering knowledge.

Sources:

```text
Runbooks
Architecture documents
API documentation
Database documentation
Postmortems
Previous incidents
```

The agent uses the RAG pipeline.

---

# 15. Root Cause Agent

The Root Cause Agent receives:

```text
Incident
+
Log findings
+
Metric findings
+
Code findings
+
Knowledge findings
+
Historical incidents
```

It produces:

```json
{
  "root_cause": "...",
  "confidence": 0.91,
  "evidence_ids": [
    "log_123",
    "metric_392",
    "commit_8a92bc",
    "doc_14"
  ],
  "alternative_hypotheses": [
    {
      "hypothesis": "Traffic spike",
      "status": "rejected",
      "reason": "Request volume remained normal."
    }
  ]
}
```

The agent must not claim certainty when evidence is insufficient.

---

# 16. Remediation Agent

### Responsibility

Generate a safe remediation plan.

It may:

- Identify affected files
- Propose code changes
- Generate a patch
- Explain expected impact
- Identify risks
- Request approval

It must not deploy directly to production.

---

# 17. Testing Agent

After a proposed code change:

```text
Patch
 ↓
Sandbox
 ↓
Build
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
Regression Tests
 ↓
Result
```

Example:

```text
142 unit tests     ✓
27 integration     ✓
Checkout test      ✓
Regression suite   ✓

Result: PASS
```

If tests fail:

```text
Testing Agent
     ↓
Failure Report
     ↓
Remediation Agent
     ↓
Revised Patch
     ↓
Testing Agent
```

This loop must have a maximum iteration limit.

---

# 18. MCP Architecture

MCP is used as the controlled interface between agents and external systems.

```text
Agent
  │
  ▼
MCP Tool
  │
  ▼
MCP Server
  │
  ▼
External System
```

## MCP Servers

```text
mcp/
├── github/
├── logs/
├── metrics/
├── database/
└── documentation/
```

---

# 19. GitHub MCP

Possible tools:

```text
get_repository()
search_code()
get_file()
get_commit()
get_diff()
get_issue()
get_pull_request()
create_branch()
commit_changes()
create_pull_request()
```

Write operations should require authorization.

---

# 20. Logging MCP

The first implementation should use a simulated log store.

Possible backend:

```text
JSON
or
PostgreSQL
```

Tools:

```text
search_logs()
get_error_trace()
get_recent_errors()
get_request_logs()
```

Future implementations may connect to:

```text
Loki
Elasticsearch
Cloud logging systems
```

The agent remains unchanged because it interacts through the MCP tool contract.

---

# 21. Metrics MCP

The demo environment exposes synthetic monitoring data.

Tools:

```text
get_metric()
get_metric_history()
get_service_health()
compare_time_windows()
```

Future adapters can connect to real monitoring platforms.

---

# 22. Database MCP

The Database MCP should initially expose strictly controlled read-only operations.

```text
inspect_schema()
describe_table()
run_readonly_query()
get_database_stats()
```

Arbitrary write queries must be blocked.

---

# 23. Documentation MCP

Tools:

```text
search_documentation()
get_document()
list_runbooks()
get_runbook()
```

The underlying storage can initially be local documents or PostgreSQL.

---

# 24. RAG Architecture

```text
Documents
   ↓
Parsing
   ↓
Cleaning
   ↓
Chunking
   ↓
Metadata
   ↓
Embeddings
   ↓
pgvector
   ↓
Retriever
   ↓
Optional Reranker
   ↓
Relevant Context
   ↓
Agent
```

Metadata should include:

```text
document_id
document_type
service
version
source
created_at
chunk_id
```

---

# 25. Memory Architecture

TraceForge uses multiple forms of memory.

## Working Memory

Current LangGraph state.

```text
incident
findings
evidence
hypotheses
current_task
```

## Persistent Memory

PostgreSQL.

```text
past incidents
investigation reports
agent runs
approvals
remediation results
```

## Semantic Memory

pgvector.

```text
past incidents
postmortems
runbooks
engineering documents
```

---

# 26. Data Model

Core entities:

```text
User
Project
Incident
Investigation
AgentRun
ToolCall
Evidence
Hypothesis
RootCause
RemediationPlan
Approval
EvaluationRun
AuditLog
```

Conceptual relationships:

```text
Project
  ├── Incidents
  │      └── Investigation
  │             ├── AgentRuns
  │             ├── Evidence
  │             ├── Hypotheses
  │             ├── RootCause
  │             └── RemediationPlan
  │
  └── Knowledge
```

---

# 27. Example Investigation State

```python
{
    "incident_id": "INC-1024",
    "status": "investigating",

    "incident": {
        "title": "...",
        "description": "...",
        "service": "checkout-api",
        "severity": "HIGH"
    },

    "tasks": [],
    "completed_tasks": [],

    "evidence": [],
    "hypotheses": [],

    "agent_findings": [],

    "root_cause": None,
    "remediation_plan": None,

    "approval": None,

    "iteration_count": 0
}
```

---

# 28. Investigation State Machine

```text
CREATED
   ↓
PLANNING
   ↓
INVESTIGATING
   ↓
EVIDENCE_COLLECTION
   ↓
CORRELATING
   ↓
ROOT_CAUSE_IDENTIFIED
   ↓
REMEDIATION_PLANNED
   ↓
AWAITING_APPROVAL
   ↓
PATCH_GENERATED
   ↓
TESTING
   ├── FAIL → REPAIR
   │            ↓
   │         TESTING
   │
   └── PASS
        ↓
     PR_CREATED
        ↓
     COMPLETED
```

Failure states:

```text
FAILED
CANCELLED
TIMEOUT
INSUFFICIENT_EVIDENCE
```

---

# 29. Async Architecture

Long-running investigations must not block HTTP requests.

```text
Client
  │
  ▼
POST /incidents
  │
  ▼
FastAPI
  │
  ├── Create incident
  └── Queue investigation
             │
             ▼
           Redis
             │
             ▼
          Worker
             │
             ▼
         LangGraph
```

The frontend subscribes to investigation events.

---

# 30. Real-Time Events

Use Server-Sent Events initially.

Example endpoint:

```http
GET /api/incidents/{incident_id}/events
```

Events:

```text
investigation.started
agent.started
tool.started
tool.completed
evidence.created
agent.completed
root_cause.updated
approval.required
testing.started
testing.completed
pr.created
investigation.completed
```

---

# 31. Guardrails

Guardrails exist at three levels.

## Input Guardrails

Detect:

- Prompt injection
- Malicious instructions
- Oversized inputs
- Invalid incident data
- Sensitive information where appropriate

## Output Guardrails

Validate:

- Structured schema
- Evidence references
- Confidence ranges
- Unsafe claims
- Required fields

## Tool Guardrails

Control:

- Which agent may call which tool
- Read vs write permissions
- Argument validation
- Rate limits
- Maximum execution time
- Human approval requirements

---

# 32. Tool Permission Matrix

| Tool | Read | Write | Approval |
|---|---:|---:|---:|
| search_logs | ✓ | — | No |
| get_metrics | ✓ | — | No |
| search_code | ✓ | — | No |
| get_commit | ✓ | — | No |
| get_database_stats | ✓ | — | No |
| run_readonly_query | ✓ | — | No |
| create_branch | — | ✓ | Yes |
| commit_changes | — | ✓ | Yes |
| create_pull_request | — | ✓ | Yes |
| database mutation | — | ✓ | Blocked by default |
| production deployment | — | ✓ | Blocked |

---

# 33. Sandbox Architecture

Generated code must be tested in an isolated environment.

```text
Agent
  ↓
Generated Patch
  ↓
Sandbox Container
  ↓
Build
  ↓
Tests
  ↓
Results
```

The sandbox should have:

- CPU limits
- Memory limits
- Execution timeout
- Restricted network
- Temporary filesystem
- No production credentials

---

# 34. Evaluation Framework

Evaluation is a first-class subsystem.

The project should contain a dataset of known incidents.

Example:

```text
incident_001
incident_002
...
incident_100
```

Each scenario contains:

```json
{
  "incident": "...",
  "ground_truth_root_cause": "...",
  "expected_evidence": [],
  "expected_tools": [],
  "expected_remediation": "..."
}
```

---

# 35. Evaluation Metrics

## Root Cause Accuracy

Did the system identify the correct root cause?

## Evidence Grounding

Are important claims supported by retrieved evidence?

## Evidence Citation Accuracy

Do cited evidence IDs actually support the claim?

## Tool Selection Accuracy

Did the agent select appropriate tools?

## Tool Argument Accuracy

Did it provide valid arguments?

## Task Completion Rate

Did it complete the investigation?

## Hallucination Rate

How frequently did it make unsupported claims?

## Safety Violations

Did the agent attempt prohibited operations?

## Latency

How long did an investigation take?

## Token Usage

How many tokens were consumed?

## Cost

Applicable when using paid models.

---

# 36. Evaluation Regression

Every significant agent change should be evaluated.

Example:

```text
Current version

Root Cause Accuracy: 87%

New version

Root Cause Accuracy: 79%

REGRESSION DETECTED
```

A production deployment can be blocked if evaluation performance falls below predefined thresholds.

---

# 37. Observability

Use structured logs and OpenTelemetry.

Every investigation should produce a trace.

Example:

```text
Incident #1024
│
├── Supervisor
│   └── LLM call
│
├── Log Agent
│   ├── search_logs
│   └── get_error_trace
│
├── Metrics Agent
│   └── get_metric_history
│
├── Code Agent
│   ├── get_commit
│   └── get_diff
│
└── Root Cause Agent
    └── LLM call
```

Track:

```text
latency
tokens
errors
retries
tool calls
agent transitions
```

---

# 38. Failure Recovery

Agents are unreliable distributed components.

The system must handle:

```text
LLM timeout
Tool timeout
MCP server failure
Malformed model output
Rate limits
Temporary database failure
Agent loop
Conflicting findings
Insufficient evidence
```

Strategies:

```text
Retry
Backoff
Timeout
Fallback
Checkpoint
Iteration budget
Human escalation
```

---

# 39. Agent Loop Protection

Every investigation has:

```text
max_iterations
max_tool_calls
max_execution_time
max_token_budget
```

Example:

```python
MAX_ITERATIONS = 30
MAX_TOOL_CALLS = 100
MAX_DURATION_SECONDS = 300
```

If limits are reached:

```text
Investigation → HUMAN_REVIEW_REQUIRED
```

---

# 40. API Design

Initial API surface:

```text
POST   /api/projects
GET    /api/projects/{id}

POST   /api/incidents
GET    /api/incidents
GET    /api/incidents/{id}

POST   /api/incidents/{id}/investigate
GET    /api/incidents/{id}/events

GET    /api/incidents/{id}/evidence
GET    /api/incidents/{id}/report

POST   /api/incidents/{id}/approve
POST   /api/incidents/{id}/reject

GET    /api/incidents/{id}/remediation
POST   /api/incidents/{id}/remediation/test

GET    /api/evaluations
POST   /api/evaluations/run

GET    /api/health
```

---

# 41. Frontend Pages

```text
/
├── landing
│
├── dashboard
│
├── projects
│   └── [project_id]
│
├── incidents
│   ├── list
│   └── [incident_id]
│
├── investigations
│   └── [investigation_id]
│
├── evaluations
│
├── agents
│
├── tools
│
└── settings
```

---

# 42. Incident Dashboard

The incident page should contain:

```text
Header
├── Incident ID
├── Severity
├── Service
└── Status

Investigation Timeline

Agent Activity

Evidence

Root Cause

Alternative Hypotheses

Remediation

Testing

Approval

Pull Request
```

---

# 43. Demo Environment

The demo environment is essential for recruiter/interviewer accessibility.

It should include predefined scenarios:

```text
1. Database Connection Exhaustion
2. Redis Failure
3. Payment API Timeout
4. Bad Deployment
5. Memory Leak
6. Database Schema Mismatch
7. Authentication Failure
8. Elevated API Latency
```

Each scenario should have:

```text
Known root cause
Known evidence
Known expected investigation path
Known remediation
```

---

# 44. Example Demo

User selects:

```text
Demo Incident #04

"Checkout API returning 500 errors"
```

TraceForge investigates.

Expected flow:

```text
Supervisor
    ↓
Log Agent
    ↓
Metrics Agent
    ↓
Code Agent
    ↓
Knowledge Agent
    ↓
Evidence Correlation
    ↓
Root Cause
    ↓
Remediation
    ↓
Human Approval
    ↓
Sandbox Testing
    ↓
GitHub PR
```

This complete flow should be reproducible.

---

# 45. Security Model

Security is a core design concern because the product interacts with source code and infrastructure.

Requirements:

```text
Authentication
Authorization
RBAC
Tool-level permissions
Secret management
Audit logging
Sandbox execution
Rate limiting
Input validation
Output validation
Network restrictions
```

Secrets must never be inserted into prompts.

---

# 46. Audit Logging

Record security-sensitive actions.

Example:

```json
{
  "actor": "agent",
  "action": "create_pull_request",
  "incident_id": "INC-1024",
  "tool": "github.create_pull_request",
  "approved_by": "user_123",
  "timestamp": "..."
}
```

---

# 47. Technology Stack

## Frontend

```text
Next.js
TypeScript
Tailwind CSS
shadcn/ui
TanStack Query
Server-Sent Events
```

## Backend

```text
Python
FastAPI
Pydantic
```

## Agent System

```text
LangGraph
LangChain
Gemini
MCP
```

## Data

```text
PostgreSQL
pgvector
Redis
```

## Async

```text
Celery
```

## Observability

```text
OpenTelemetry
Structured Logging
LangSmith (optional)
```

## Infrastructure

```text
Docker
GitHub Actions
Cloud deployment
```

## Testing

```text
Pytest
Playwright
```

---

# 48. Repository Structure

```text
traceforge/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── types/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── workers/
│
├── agents/
│   ├── supervisor/
│   ├── log_agent/
│   ├── metrics_agent/
│   ├── code_agent/
│   ├── knowledge_agent/
│   ├── root_cause_agent/
│   ├── remediation_agent/
│   └── testing_agent/
│
├── graph/
│   ├── state.py
│   ├── nodes.py
│   ├── edges.py
│   └── workflow.py
│
├── mcp/
│   ├── github/
│   ├── logs/
│   ├── metrics/
│   ├── database/
│   └── documentation/
│
├── rag/
│   ├── ingestion/
│   ├── chunking/
│   ├── embeddings/
│   ├── retrieval/
│   └── reranking/
│
├── memory/
│
├── guardrails/
│   ├── input/
│   ├── output/
│   └── tools/
│
├── evaluation/
│   ├── datasets/
│   ├── evaluators/
│   ├── metrics/
│   ├── experiments/
│   └── reports/
│
├── simulator/
│   ├── ecommerce/
│   ├── incidents/
│   ├── logs/
│   ├── metrics/
│   └── failures/
│
├── sandbox/
│
├── observability/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── agent/
│   └── e2e/
│
├── docs/
│   ├── architecture.md
│   ├── agent-design.md
│   ├── evaluation.md
│   ├── security.md
│   └── failure-modes.md
│
├── docker-compose.yml
├── .env.example
├── DESIGN.md
└── README.md
```

---

# 49. Development Strategy

Do not implement the entire architecture at once.

Build vertically.

## Phase 0 — Architecture

Define:

```text
Incident
Agent
Tool
Evidence
Investigation
```

---

## Phase 1 — Single Agent

Build:

```text
Incident
 ↓
Agent
 ↓
Log Tool
 ↓
Root Cause
```

Use simulated logs.

Goal:

> One incident can be investigated end-to-end.

---

## Phase 2 — LangGraph

Introduce:

```text
State
Nodes
Edges
Conditional Routing
Persistence
```

---

## Phase 3 — Multi-Agent

Add:

```text
Supervisor
Log Agent
Metrics Agent
Code Agent
Knowledge Agent
Root Cause Agent
```

---

## Phase 4 — RAG

Add:

```text
Runbooks
Postmortems
Architecture docs
Past incidents
```

---

## Phase 5 — MCP

Move external interactions behind MCP servers.

---

## Phase 6 — Deep Agent Behavior

Add:

```text
Planning
Task decomposition
Delegation
Long-running tasks
Dynamic tool selection
Failure recovery
```

---

## Phase 7 — Remediation

Add:

```text
Patch generation
Sandbox testing
Human approval
GitHub PR
```

---

## Phase 8 — Guardrails

Add:

```text
Input validation
Output validation
Tool permissions
Approval gates
Execution limits
```

---

## Phase 9 — Evaluation

Build:

```text
50–100 known incidents
Ground truth
Automated evaluation
Regression testing
```

---

## Phase 10 — Production Engineering

Add:

```text
Redis
Celery
Observability
Authentication
RBAC
Rate limiting
Docker
CI/CD
Deployment
```

---

# 50. MVP Definition

The MVP is complete when:

```text
User
 ↓
Creates incident
 ↓
Supervisor
 ↓
Log Agent
 ↓
Retrieves logs
 ↓
Root Cause Agent
 ↓
Produces evidence-backed diagnosis
 ↓
Frontend displays investigation
```

The MVP does NOT require:

```text
Real production infrastructure
Multiple cloud providers
Automatic deployment
Kubernetes
Complex distributed architecture
```

---

# 51. V1 Definition

V1 should support:

```text
✓ Multi-agent investigation
✓ Logs
✓ Metrics
✓ GitHub
✓ RAG
✓ Memory
✓ MCP
✓ LangGraph
✓ Live investigation timeline
✓ Root-cause report
✓ Guardrails
✓ Human approval
```

---

# 52. V2 Definition

V2 should support:

```text
✓ Remediation generation
✓ Sandbox execution
✓ Automated testing
✓ Pull request generation
✓ Evaluation benchmark
✓ Agent tracing
✓ Failure recovery
✓ Authentication
✓ RBAC
✓ Production deployment
```

---

# 53. Success Metrics

The project should measure itself.

Product metrics:

```text
Investigation completion rate
Average investigation duration
Average number of tool calls
Average number of agents used
```

AI metrics:

```text
Root cause accuracy
Evidence grounding
Citation accuracy
Tool selection accuracy
Task completion
Hallucination rate
Safety violation rate
```

Engineering metrics:

```text
API latency
Agent latency
LLM latency
Failure rate
Retry rate
Token usage
Cost
```

---

# 54. Important Design Decisions

## Why LangGraph?

Because TraceForge requires:

- Stateful workflows
- Multi-agent orchestration
- Conditional routing
- Persistence
- Human approval
- Long-running execution

---

## Why MCP?

Because tools should be exposed through standardized interfaces instead of tightly coupling every agent to individual APIs.

---

## Why PostgreSQL + pgvector?

Because TraceForge requires both:

```text
Relational application data
+
Semantic retrieval
```

Using one primary database reduces unnecessary infrastructure complexity.

---

## Why Redis?

Because agent investigations are asynchronous and require:

```text
queues
caching
temporary state
coordination
```

---

## Why a Simulator?

A public AI system cannot depend on a recruiter's private production environment.

The simulator gives:

```text
Reproducibility
Known ground truth
Safe experimentation
Automated evaluation
Instant demos
```

---

# 55. Non-Goals

TraceForge is NOT initially intended to:

```text
Automatically deploy to production
Replace human SREs
Manage arbitrary cloud infrastructure
Execute unrestricted shell commands
Guarantee root-cause correctness
Act as a fully autonomous production operator
```

The system is an **AI investigation and remediation assistant with controlled autonomy**.

---

# 56. Final System Concept

The final TraceForge system can be summarized as:

```text
                  ┌───────────────────┐
                  │      INCIDENT     │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │     SUPERVISOR    │
                  └─────────┬─────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
          LOG AGENT     CODE AGENT    METRICS AGENT
              │             │              │
              ▼             ▼              ▼
          LOG MCP       GITHUB MCP      METRICS MCP
              │             │              │
              └─────────────┼──────────────┘
                            ▼
                    ┌───────────────┐
                    │   KNOWLEDGE   │
                    │  RAG + MEMORY │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │  ROOT CAUSE   │
                    │     AGENT     │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ REMEDIATION   │
                    │     AGENT     │
                    └───────┬───────┘
                            ▼
                       GUARDRAILS
                            │
                            ▼
                    HUMAN APPROVAL
                            │
                            ▼
                    TESTING SANDBOX
                            │
                            ▼
                       GITHUB PR
```

---

# 57. The Core Engineering Principle

TraceForge should never be:

```text
User
 ↓
LLM
 ↓
Answer
```

It should be:

```text
User
 ↓
Agent System
 ↓
Tools
 ↓
External Evidence
 ↓
Structured State
 ↓
Multiple Specialized Agents
 ↓
Evidence Correlation
 ↓
Evaluation
 ↓
Controlled Action
 ↓
Human Approval
 ↓
Verified Result
```

That distinction is the foundation of the project.

---

# 58. Definition of Done

TraceForge is considered portfolio-ready when a recruiter can open the deployed application and:

1. Select the demo environment.
2. Select a realistic incident.
3. Start an investigation.
4. Watch multiple agents investigate.
5. Inspect the evidence they retrieved.
6. See the root-cause report.
7. See confidence and supporting evidence.
8. Review the proposed remediation.
9. Approve the change.
10. Watch sandbox tests execute.
11. See the generated GitHub pull request.
12. Open the evaluation dashboard.
13. See benchmark results.
14. Open the architecture documentation.
15. Understand how MCP, LangGraph, RAG, memory, guardrails, evaluation, and observability work together.

The final product should make the following statement demonstrable:

> **"I didn't just build an LLM application. I designed, evaluated, secured, observed, and deployed an agentic AI system that performs a realistic engineering workflow."**
