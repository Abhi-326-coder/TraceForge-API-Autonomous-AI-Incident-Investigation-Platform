# TraceForge — UI Design Specification

> **Autonomous AI Incident Investigation & Remediation Platform**
>
> This document defines the user interface and user experience for TraceForge. The UI should communicate that TraceForge is an engineering operations product powered by agents—not a generic AI chatbot.

---

# 1. UI Vision

TraceForge should feel like an **AI-powered incident command center**.

The primary visual idea is:

```text
INCIDENT
   ↓
INVESTIGATION
   ↓
EVIDENCE
   ↓
ROOT CAUSE
   ↓
REMEDIATION
   ↓
VALIDATION
   ↓
PULL REQUEST
```

The UI should make this workflow visible.

The user should always know:

- What is happening?
- Which agent is working?
- What evidence was found?
- What has been concluded?
- What is uncertain?
- What action is proposed?
- Does the AI need human approval?
- What happened after approval?

---

# 2. Design Principles

## 2.1 Not a Chatbot

The primary interface must NOT be:

```text
┌────────────────────────────┐
│ Ask TraceForge anything... │
└────────────────────────────┘
```

The primary interface is an investigation workspace.

Chat can exist as a secondary interaction for asking questions about the current incident.

---

## 2.2 Evidence Before Conclusions

The interface should prioritize:

```text
Evidence
  ↓
Finding
  ↓
Conclusion
```

rather than:

```text
AI says...
```

---

## 2.3 Progressive Disclosure

The user should see the important information first.

### Level 1

```text
Incident
Status
Root Cause
Confidence
Action
```

### Level 2

```text
Evidence
Agent activity
Timeline
```

### Level 3

```text
Tool calls
Raw logs
Commit diffs
Retrieved documents
Evaluation details
```

---

## 2.4 Human Control

The interface must make AI autonomy boundaries obvious.

Use visual states:

```text
✓ Autonomous
⚠ Approval Required
🔒 Blocked
```

Never make an irreversible action look like a normal button.

---

# 3. Visual Identity

TraceForge is an engineering tool.

Recommended visual direction:

```text
Dark-first
High contrast
Technical
Minimal
Dense but readable
Data-oriented
Professional
```

Avoid:

- Excessive gradients
- Cartoon AI imagery
- Huge decorative illustrations
- Excessive rounded cards
- Chatbot-style bubbles everywhere
- Excessive animations

---

# 4. Color System

Use semantic colors rather than decorative colors.

```text
Background:
Near-black / deep slate

Surface:
Dark slate

Border:
Subtle gray

Primary:
Electric blue / indigo

Success:
Green

Warning:
Amber

Critical:
Red

Information:
Blue
```

Semantic mapping:

| State | Meaning |
|---|---|
| Blue | Active / investigating |
| Green | Success / resolved |
| Amber | Warning / approval |
| Red | Critical / failure |
| Gray | Inactive / unavailable |
| Purple | AI-generated / agent-related |

Do not use color alone to communicate meaning. Pair color with text/icons.

---

# 5. Typography

Recommended:

```text
Primary:
Inter / Geist

Monospace:
JetBrains Mono
```

Use monospace for:

- Logs
- Code
- Tool calls
- IDs
- Metrics
- API endpoints

Use normal UI typography for:

- Reports
- Explanations
- Navigation
- Labels

---

# 6. Application Layout

Desktop layout:

```text
┌─────────────────────────────────────────────────────────────┐
│ TraceForge                         Search   Notifications   │
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│  Dashboard    │                                             │
│               │                                             │
│  Incidents    │              Main Workspace                 │
│               │                                             │
│  Projects     │                                             │
│               │                                             │
│  Evaluations  │                                             │
│               │                                             │
│  Agents       │                                             │
│               │                                             │
│  Tools        │                                             │
│               │                                             │
│  Settings     │                                             │
│               │                                             │
├───────────────┤                                             │
│ User          │                                             │
└───────────────┴─────────────────────────────────────────────┘
```

---

# 7. Navigation

Primary sidebar:

```text
TraceForge

Overview
Incidents
Projects
Evaluations

AI Runtime
  Agents
  Tools
  Memory

System
  Activity
  Settings
```

The sidebar should remain visible on desktop.

On mobile it becomes a drawer.

---

# 8. Global Header

Header:

```text
┌──────────────────────────────────────────────────────────────┐
│ TraceForge    Search...        ● System Healthy   User       │
└──────────────────────────────────────────────────────────────┘
```

Elements:

### Search

Search:

- Incidents
- Projects
- Evidence
- PRs
- Documentation

### System Status

Example:

```text
● All systems operational
```

or:

```text
⚠ Agent runtime degraded
```

### User Menu

Contains:

```text
Profile
Organization
Preferences
Logout
```

---

# 9. Landing Page

The landing page should immediately communicate the product.

Hero:

```text
AUTONOMOUS INCIDENT INVESTIGATION

Your AI engineering team
for production incidents.

TraceForge investigates logs, metrics, code and
documentation, identifies probable root causes,
and prepares validated remediation.

[ Try Demo ]     [ View Architecture ]
```

---

# 10. Landing Page Architecture

Sections:

```text
Hero
 ↓
How it works
 ↓
Live investigation preview
 ↓
Agent architecture
 ↓
Evaluation metrics
 ↓
Safety model
 ↓
Technology
 ↓
Demo CTA
```

---

# 11. Hero Section

The hero should not use generic AI artwork.

Instead show a mini live investigation panel.

Example:

```text
┌───────────────────────────────────────────────┐
│ INCIDENT #1024                         HIGH   │
│ Checkout API returning 500s                  │
│                                               │
│ ✓ Logs analyzed                               │
│ ✓ Metrics correlated                          │
│ ✓ Recent commit identified                    │
│ ● Root cause analysis                         │
│                                               │
│ Root Cause Confidence: 91%                    │
└───────────────────────────────────────────────┘
```

This immediately demonstrates what the product does.

---

# 12. Demo CTA

Primary CTA:

```text
Try Live Demo
```

Secondary CTA:

```text
Explore Architecture
```

The demo should launch directly into a preconfigured environment.

---

# 13. Dashboard

The dashboard answers:

> "What is happening across my projects right now?"

Layout:

```text
┌──────────────────────────────────────────────────────────┐
│ Overview                                                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Active Incidents    Investigations    Resolved          │
│       3                  7              24               │
│                                                          │
├──────────────────────────────────────────────────────────┤
│ Active Incidents                                         │
│                                                          │
│ 🔴 INC-1024  Checkout failures      Investigating       │
│ 🟠 INC-1023  API latency            Awaiting approval   │
│ 🟢 INC-1022  Redis timeout           Resolved           │
│                                                          │
├──────────────────────────────┬───────────────────────────┤
│ Agent Runtime                │ System Health             │
│                              │                           │
│ 8 active agents              │ API       ● Healthy       │
│ 42 tool calls                │ Redis     ● Healthy       │
│ 3 investigations             │ DB        ● Healthy       │
└──────────────────────────────┴───────────────────────────┘
```

---

# 14. Dashboard Metrics

Show only useful metrics.

Recommended:

```text
Active incidents
Investigations running
Resolved incidents
Average investigation time
Root-cause accuracy
Agent success rate
```

Do not overload the dashboard with meaningless AI statistics.

---

# 15. Incident List

Page:

```text
/incidents
```

Table:

```text
┌──────────┬─────────────────────┬─────────┬──────────────┬─────────────┐
│ ID       │ Incident            │ Service │ Severity     │ Status      │
├──────────┼─────────────────────┼─────────┼──────────────┼─────────────┤
│ INC-1024 │ Checkout failures   │ checkout│ 🔴 HIGH      │ Investigating│
│ INC-1023 │ API latency         │ api     │ 🟠 MEDIUM    │ Approval    │
│ INC-1022 │ Redis timeout       │ cache   │ 🟢 LOW       │ Resolved    │
└──────────┴─────────────────────┴─────────┴──────────────┴─────────────┘
```

Filters:

```text
Severity
Status
Service
Project
Date
```

---

# 16. Create Incident

Primary button:

```text
+ New Incident
```

Form:

```text
┌──────────────────────────────────────────────┐
│ Create Incident                              │
├──────────────────────────────────────────────┤
│                                              │
│ Title                                        │
│ [ Checkout API returning 500 errors        ] │
│                                              │
│ Description                                  │
│ ┌──────────────────────────────────────────┐ │
│ │ Customers cannot complete checkout.      │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ Project                                      │
│ [ Demo E-Commerce                       ▼ ] │
│                                              │
│ Service                                      │
│ [ checkout-api                          ▼ ] │
│                                              │
│ Severity                                     │
│ [ HIGH                                   ▼ ] │
│                                              │
│          [ Cancel ] [ Start Investigation ]  │
└──────────────────────────────────────────────┘
```

---

# 17. Incident Detail Page

This is the most important screen.

URL:

```text
/incidents/[incident_id]
```

Layout:

```text
┌─────────────────────────────────────────────────────────────┐
│ ← Incidents                                                │
│                                                             │
│ INC-1024                       🔴 HIGH     ● INVESTIGATING  │
│ Checkout API returning 500 errors                           │
│ checkout-api · Demo E-Commerce                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Overview] [Investigation] [Evidence] [Remediation]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 18. Incident Header

Header contains:

```text
Incident ID
Title
Severity
Service
Project
Created time
Current status
```

Actions:

```text
Pause
Cancel
View report
```

Do not show destructive actions prominently.

---

# 19. Investigation Workspace

Main investigation screen:

```text
┌────────────────────────────┬────────────────────────────────┐
│ Agent Activity             │ Investigation Summary          │
│                            │                                │
│ ✓ Supervisor               │ Status: Investigating          │
│ ✓ Log Agent                │                                │
│ ✓ Metrics Agent            │ Root Cause: Pending            │
│ ● Code Agent               │                                │
│                            │ Evidence: 42                   │
│ ○ Root Cause Agent         │ Agents: 5                      │
│                            │                                │
├────────────────────────────┴────────────────────────────────┤
│ Investigation Timeline                                      │
│                                                             │
│ 10:31 Supervisor created plan                               │
│ 10:32 Log Agent retrieved 1,204 logs                        │
│ 10:32 Metrics Agent analyzed 6 metrics                     │
│ 10:33 Code Agent found recent commit                        │
│ 10:33 Knowledge Agent retrieved 3 runbooks                  │
│ 10:34 Root Cause Agent correlating evidence                 │
└─────────────────────────────────────────────────────────────┘
```

---

# 20. Agent Status

Every agent should have a clear state.

```text
○ Queued
● Running
✓ Completed
⚠ Failed
⏸ Paused
```

Example:

```text
Log Agent
✓ Completed
1,204 logs
842ms
```

---

# 21. Agent Detail Drawer

Clicking an agent opens a drawer.

```text
┌───────────────────────────────────────────┐
│ Log Agent                             ×   │
├───────────────────────────────────────────┤
│ Status: ✓ Completed                       │
│ Duration: 4.2s                            │
│ Tool calls: 3                             │
│                                           │
│ Actions                                   │
│                                           │
│ ✓ search_logs                             │
│ ✓ get_error_trace                         │
│ ✓ get_recent_errors                       │
│                                           │
│ Findings                                  │
│ Database connection pool exhausted.       │
│                                           │
│ Evidence                                  │
│ [evidence_123] [evidence_127]             │
└───────────────────────────────────────────┘
```

Never expose hidden chain-of-thought.

Show actions, outputs, evidence, and concise explanations.

---

# 22. Live Investigation Timeline

The timeline is one of the signature UI elements.

```text
● Supervisor
  Investigation plan created
              │
              ▼
● Log Agent
  1,204 logs retrieved
              │
              ▼
● Metrics Agent
  DB connections increased 42 → 98
              │
              ▼
● Code Agent
  Commit 8a92bc identified
              │
              ▼
● Knowledge Agent
  Checkout runbook retrieved
              │
              ▼
● Root Cause Agent
  Correlating evidence...
```

Timeline entries should be expandable.

---

# 23. Evidence Panel

Evidence should be a first-class object.

```text
┌─────────────────────────────────────────────────────────┐
│ Evidence                                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ [LOG] Database connection pool exhausted                │
│ Source: checkout-api                                    │
│ 10:29:32                                                 │
│                                                         │
│ [METRIC] DB connections                                 │
│ Current: 98 / 100                                       │
│ Baseline: 42                                            │
│                                                         │
│ [GITHUB] Commit 8a92bc                                   │
│ "Refactor checkout transaction handling"                │
│                                                         │
│ [RUNBOOK] checkout.md                                   │
│ Payment calls must not occur inside DB transactions.    │
└─────────────────────────────────────────────────────────┘
```

---

# 24. Evidence Detail

Clicking evidence opens:

```text
┌───────────────────────────────────────────┐
│ Evidence #evidence_123                ×   │
├───────────────────────────────────────────┤
│ Type                                      │
│ LOG                                       │
│                                           │
│ Source                                    │
│ Logging MCP                               │
│                                           │
│ Service                                   │
│ checkout-api                              │
│                                           │
│ Timestamp                                 │
│ 2026-10-02 10:29:32                      │
│                                           │
│ Raw Evidence                              │
│ ┌───────────────────────────────────────┐ │
│ │ ERROR Database connection pool...     │ │
│ └───────────────────────────────────────┘ │
│                                           │
│ Used by                                   │
│ Root Cause Agent                          │
└───────────────────────────────────────────┘
```

---

# 25. Root Cause Card

When root cause is available:

```text
┌───────────────────────────────────────────────────────┐
│ ROOT CAUSE                                             │
├───────────────────────────────────────────────────────┤
│                                                       │
│ Checkout transaction scope regression                 │
│                                                       │
│ Confidence                                             │
│ ████████████████████░░ 91%                            │
│                                                       │
│ Summary                                                │
│ Database connections remain occupied while the        │
│ checkout service waits for the payment provider.      │
│                                                       │
│ Supporting Evidence                                   │
│ ✓ Database pool saturation                            │
│ ✓ Recent transaction change                            │
│ ✓ Matching application errors                         │
│ ✓ Checkout runbook                                    │
│                                                       │
│ [ View Evidence ]                                     │
└───────────────────────────────────────────────────────┘
```

---

# 26. Confidence Visualization

Do not imply statistical certainty when confidence is only an LLM estimate.

Label it:

```text
Model confidence
```

rather than:

```text
91% probability this is definitely correct
```

Use:

```text
High
Medium
Low
```

alongside the numeric model confidence if available.

---

# 27. Alternative Hypotheses

The interface should show rejected hypotheses.

```text
Alternative Hypotheses

✓ Database transaction regression
   Supported by 4 evidence sources

✗ Traffic spike
   Rejected — request volume remained normal

✗ Redis outage
   Rejected — Redis health remained normal
```

This demonstrates that the agent investigated alternatives.

---

# 28. Uncertainty Panel

If evidence is incomplete:

```text
┌────────────────────────────────────────────┐
│ ⚠ Investigation Uncertainty               │
├────────────────────────────────────────────┤
│ GitHub source could not be accessed.       │
│                                            │
│ Root cause confidence is limited.          │
│                                            │
│ Recommended action:                        │
│ Connect repository or provide source.      │
└────────────────────────────────────────────┘
```

Never hide missing evidence.

---

# 29. Remediation Tab

Before approval:

```text
┌───────────────────────────────────────────────────────┐
│ Proposed Remediation                                  │
├───────────────────────────────────────────────────────┤
│                                                       │
│ Move external payment call outside DB transaction.   │
│                                                       │
│ Risk: MEDIUM                                          │
│                                                       │
│ Affected files                                        │
│ PaymentService.java                                   │
│                                                       │
│ Expected impact                                       │
│ Reduce DB connection occupancy during payment calls. │
│                                                       │
│ Validation                                            │
│ Unit tests                                             │
│ Integration tests                                     │
│ Checkout regression test                              │
│                                                       │
│              [ Reject ]  [ Review & Approve ]          │
└───────────────────────────────────────────────────────┘
```

---

# 30. Approval Modal

Approval must be explicit.

```text
┌──────────────────────────────────────────────┐
│ Approve Remediation                       ×  │
├──────────────────────────────────────────────┤
│                                              │
│ Action                                       │
│ Create branch and commit proposed patch      │
│                                              │
│ Risk                                         │
│ MEDIUM                                       │
│                                              │
│ Tests                                        │
│ Not executed yet                             │
│                                              │
│ This action will modify the connected        │
│ repository.                                  │
│                                              │
│ [ Cancel ]          [ Approve Action ]       │
└──────────────────────────────────────────────┘
```

The button should not say simply:

```text
OK
```

It should describe the action.

---

# 31. Code Diff Viewer

Use a real diff viewer.

```text
PaymentService.java

- transaction {
-     paymentService.charge()
- }

+ paymentService.charge()
+
+ transaction {
+     orderRepository.save()
+ }
```

Features:

```text
Line numbers
Syntax highlighting
Expand context
Copy
Open on GitHub
```

---

# 32. Testing View

After approval:

```text
┌─────────────────────────────────────────────────────────┐
│ Sandbox Validation                                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Environment: Isolated Docker Sandbox                    │
│                                                         │
│ Build                                      ✓            │
│ Unit Tests                                ✓ 142/142     │
│ Integration Tests                         ✓ 27/27      │
│ Checkout Regression                       ✓             │
│                                                         │
│ Duration: 18.4s                                         │
│                                                         │
│ RESULT: PASS                                            │
└─────────────────────────────────────────────────────────┘
```

---

# 33. Testing Failure View

If tests fail:

```text
┌─────────────────────────────────────────────────────────┐
│ Sandbox Validation                         ⚠ FAILED     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Unit Tests                                ✓ 142/142     │
│ Integration Tests                         ✗ 24/27      │
│                                                         │
│ Failure                                                 │
│ PaymentIntegrationTest                                │
│ Expected HTTP 200, received HTTP 500                   │
│                                                         │
│ [ View Logs ] [ Send Back to Remediation ]             │
└─────────────────────────────────────────────────────────┘
```

---

# 34. Pull Request View

When PR is created:

```text
┌─────────────────────────────────────────────────────────┐
│ GitHub Pull Request                                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ #184 Fix checkout transaction connection exhaustion     │
│                                                         │
│ Status: ● Ready for Review                              │
│                                                         │
│ Branch                                                   │
│ fix/checkout-db-transaction                             │
│                                                         │
│ Tests                                                     │
│ ✓ 169 passed                                             │
│                                                         │
│ AI Summary                                               │
│ Moved payment provider call outside database            │
│ transaction scope.                                     │
│                                                         │
│ [ Open GitHub PR ]                                      │
└─────────────────────────────────────────────────────────┘
```

---

# 35. Activity Page

Page:

```text
/activity
```

Shows:

```text
10:34:22 Agent created PR
10:34:10 Sandbox tests passed
10:33:41 User approved remediation
10:33:12 Root cause identified
10:32:52 Code Agent completed
```

Useful for auditability.

---

# 36. Agents Page

Page:

```text
/agents
```

Display agent cards:

```text
┌───────────────────────┐
│ Supervisor Agent      │
│                       │
│ Runs: 142             │
│ Success: 93%          │
│ Avg latency: 2.1s     │
│                       │
│ [ View Details ]      │
└───────────────────────┘
```

Agents:

```text
Supervisor
Log Agent
Metrics Agent
Code Agent
Knowledge Agent
Root Cause Agent
Remediation Agent
Testing Agent
```

---

# 37. Agent Detail Page

Show:

```text
Purpose
Allowed tools
Recent runs
Success rate
Average latency
Failure rate
Token usage
Evaluation score
```

Example:

```text
Code Agent

Allowed Tools

✓ search_code
✓ get_file
✓ get_commit
✓ get_diff

✗ create_branch
✗ commit_changes

Reason:
Read-only investigation agent.
```

This makes the security model visible.

---

# 38. Tools Page

Page:

```text
/tools
```

Display connected tools:

```text
GitHub MCP
● Connected

Logging MCP
● Connected

Metrics MCP
● Connected

Database MCP
● Connected

Documentation MCP
● Connected
```

---

# 39. Tool Detail

```text
GitHub MCP

Status:
● Connected

Tools:

search_code      READ
get_commit       READ
get_diff         READ
create_branch    WRITE
create_pr        WRITE

Permissions:
Write actions require approval.
```

---

# 40. Projects Page

Projects represent connected software systems.

```text
┌─────────────────────────────────────────────────────────┐
│ Projects                              [+ New Project]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ E-Commerce Platform                                     │
│ GitHub: connected                                       │
│ Logs: connected                                         │
│ Metrics: connected                                      │
│                                                         │
│ 12 incidents · 4 active                                │
│                                                         │
│ [ Open Project ]                                       │
└─────────────────────────────────────────────────────────┘
```

---

# 41. Project Setup Wizard

Steps:

```text
1. Project
2. GitHub
3. Logs
4. Metrics
5. Documentation
6. Review
```

Progress:

```text
●───●───○───○───○───○
1   2   3   4   5   6
```

---

# 42. Demo Mode

Demo mode should require almost no setup.

Landing:

```text
[ Launch Demo ]
```

Then:

```text
Choose Incident

○ Checkout API Failure
○ Redis Outage
○ Payment Timeout
○ Memory Leak
○ Bad Deployment
```

Button:

```text
[ Start Demo Investigation ]
```

---

# 43. Demo Environment Indicator

Always show:

```text
DEMO ENVIRONMENT
```

or:

```text
CONNECTED PROJECT
```

The user should never confuse synthetic infrastructure with real production infrastructure.

---

# 44. Evaluation Dashboard

Page:

```text
/evaluations
```

Hero metrics:

```text
┌───────────────┬───────────────┬───────────────┐
│ Root Cause    │ Evidence      │ Tool          │
│ Accuracy      │ Grounding     │ Accuracy      │
│ 87%           │ 93%           │ 91%           │
└───────────────┴───────────────┴───────────────┘
```

These values must come from actual benchmark results.

---

# 45. Evaluation Trend

Show performance over versions.

```text
Accuracy
100% ┤
 90% ┤           ╭───╮
 80% ┤      ╭────╯   ╰──╮
 70% ┤──────╯
     └────────────────────
       v0.1 v0.2 v0.3 v0.4
```

Use the chart to identify regressions.

---

# 46. Evaluation Case Explorer

```text
Incident #042

Ground Truth:
Database connection exhaustion

Agent:
Database connection exhaustion

Result:
✓ Correct

Evidence grounding:
✓

Expected tools:
✓

Unsafe actions:
0
```

---

# 47. System Health Page

Display:

```text
API                 ● Healthy
PostgreSQL          ● Healthy
Redis               ● Healthy
Agent Workers       ● Healthy
GitHub MCP          ● Healthy
Logs MCP            ● Healthy
Metrics MCP         ● Healthy
```

Clicking a service shows latency and recent errors.

---

# 48. Settings

Sections:

```text
Account
Organization
LLM Provider
Model
Agent Limits
Tool Permissions
Integrations
Security
Notifications
```

Dangerous configuration changes should require confirmation.

---

# 49. Agent Budget Settings

Allow administrators to configure:

```text
Max iterations
Max tool calls
Max investigation duration
Max token budget
```

Example:

```text
Maximum investigation duration

[ 5 minutes ]

Maximum tool calls

[ 100 ]
```

---

# 50. Empty States

Every page needs meaningful empty states.

Example:

```text
No incidents yet.

Create your first incident to start
an AI-powered investigation.

[ Create Incident ]
```

Avoid generic:

```text
Nothing here.
```

---

# 51. Loading States

Use contextual loading states.

Bad:

```text
Loading...
```

Good:

```text
● Connecting to investigation runtime...

● Supervisor is planning investigation...

● Log Agent is searching application logs...
```

---

# 52. Error States

Errors should explain:

```text
What failed
Why it may have failed
What the user can do
```

Example:

```text
⚠ GitHub connection failed

TraceForge could not access the repository.

Possible cause:
The GitHub token expired.

[ Reconnect GitHub ]
```

---

# 53. Agent Failure State

If one agent fails:

```text
⚠ Code Agent unavailable

GitHub MCP returned a timeout.

TraceForge continued using:

✓ Logs
✓ Metrics
✓ Documentation

Root cause confidence may be reduced.

[ Retry Agent ]
```

Do not make the whole UI appear broken if only one agent failed.

---

# 54. Accessibility

Requirements:

```text
Keyboard navigation
Focus states
ARIA labels
Screen reader support
Sufficient contrast
Reduced motion
Semantic HTML
```

Never rely exclusively on:

```text
red = failure
green = success
```

Use icons + labels.

---

# 55. Responsive Design

Desktop is the primary experience.

### Desktop

Three-column layouts are allowed.

### Tablet

Collapse secondary panels.

### Mobile

Prioritize:

```text
Incident
Status
Root Cause
Evidence
Approval
```

Agent details and raw logs can become drawers.

---

# 56. Mobile Layout

```text
┌─────────────────────────────┐
│ TraceForge          ☰       │
├─────────────────────────────┤
│ INC-1024                    │
│ 🔴 HIGH                     │
│ Investigating               │
│                             │
│ Root Cause                  │
│ Pending                     │
│                             │
│ Agent Activity              │
│ ✓ Logs                      │
│ ✓ Metrics                   │
│ ● Code                      │
│                             │
│ Evidence                    │
│ 42 items                    │
│                             │
│ [ View Investigation ]      │
└─────────────────────────────┘
```

---

# 57. Animation

Animations should communicate system activity.

Good:

```text
Agent status transitions
Timeline entry appearance
Progress indicators
Panel expansion
```

Avoid:

```text
Constant floating AI particles
Excessive glowing effects
Slow page transitions
Decorative loading animations
```

The product should feel fast.

---

# 58. Signature UI Element — Investigation Timeline

The investigation timeline should become a recognizable TraceForge feature.

Visual structure:

```text
        ●
        │
        │ Supervisor
        │ Plan created
        │
        ●
        │ Log Agent
        │ 1,204 logs analyzed
        │
        ●
        │ Metrics Agent
        │ DB saturation detected
        │
        ●
        │ Code Agent
        │ Recent transaction commit
        │
        ●
        │ Root Cause
        │ Diagnosis generated
```

---

# 59. Signature UI Element — Evidence Chain

Show relationships:

```text
Incident
   │
   ├── Log Evidence
   │
   ├── Metric Evidence
   │
   ├── Code Evidence
   │
   └── Documentation
          │
          ▼
      Root Cause
```

This visually communicates evidence-based reasoning.

---

# 60. Signature UI Element — Agent Network

Optional visualization:

```text
                 Supervisor
                     │
          ┌──────────┼──────────┐
          │          │          │
        Logs       Metrics     Code
          │          │          │
          └──────────┼──────────┘
                     │
                 Root Cause
                     │
                 Remediation
```

Use this sparingly.

It should explain architecture, not become decorative.

---

# 61. AI Chat — Secondary Interface

A contextual assistant can exist:

```text
┌─────────────────────────────────────────┐
│ Ask about this investigation             │
├─────────────────────────────────────────┤
│ Why do you think DB connections caused   │
│ the failure?                             │
│                                         │
│ TraceForge:                             │
│ The conclusion is supported by 4        │
│ evidence sources...                     │
└─────────────────────────────────────────┘
```

Answers should reference evidence.

Chat should not become the primary product interaction.

---

# 62. Evidence Citation UX

When the AI says:

> Database connection saturation is likely contributing to the incident.

Show:

```text
[Evidence E-123]
```

Clicking it opens the evidence.

This allows users to verify claims.

---

# 63. Status Vocabulary

Use consistent status labels.

### Incident

```text
NEW
INVESTIGATING
ROOT_CAUSE_FOUND
AWAITING_APPROVAL
REMEDIATING
VALIDATING
RESOLVED
FAILED
CANCELLED
```

### Agent

```text
QUEUED
RUNNING
COMPLETED
FAILED
PAUSED
```

### Remediation

```text
PROPOSED
APPROVAL_REQUIRED
APPROVED
TESTING
PASSED
FAILED
PR_CREATED
```

---

# 64. Notification System

Notifications should be meaningful.

Examples:

```text
✓ Investigation completed
⚠ Approval required
⚠ Agent failed
✓ Tests passed
✓ Pull request created
```

Avoid notifying users for every tool call.

---

# 65. Toast Rules

Use toasts for:

```text
Action completed
Connection established
Approval recorded
PR created
```

Use persistent panels for:

```text
Errors
Critical warnings
Approval requests
```

---

# 66. Search

Global search should support:

```text
INC-1024
checkout
payment
root cause
PR #184
evidence_123
```

Results should group by:

```text
Incidents
Projects
Evidence
Pull Requests
Documents
```

---

# 67. Keyboard Shortcuts

Optional advanced shortcuts:

```text
g d → Dashboard
g i → Incidents
g e → Evaluations
n i → New Incident
/   → Search
```

Display shortcuts in tooltips.

---

# 68. Design System Components

Reusable components:

```text
Button
Badge
StatusBadge
Card
MetricCard
Table
Tabs
Drawer
Modal
Timeline
EvidenceCard
AgentCard
AgentStatus
CodeDiff
LogViewer
MetricChart
ApprovalDialog
ProgressBar
EmptyState
ErrorState
Skeleton
Toast
CommandPalette
```

---

# 69. Component States

Every interactive component should define:

```text
Default
Hover
Focus
Active
Disabled
Loading
Error
Success
```

---

# 70. Button Hierarchy

Primary:

```text
Start Investigation
Approve Action
Create Incident
```

Secondary:

```text
View Evidence
Open GitHub
Retry
```

Danger:

```text
Reject
Cancel Investigation
Disconnect Integration
```

Destructive actions require confirmation where appropriate.

---

# 71. Tables

Tables should support:

```text
Sorting
Filtering
Pagination
Row click
Status badges
Responsive overflow
```

Avoid excessive columns.

---

# 72. Charts

Use charts only where they answer a question.

Useful:

```text
Error rate
Latency
Database connections
Agent latency
Evaluation accuracy
Investigation duration
```

Each chart should state:

```text
Metric
Time range
Units
Baseline where relevant
```

---

# 73. Logs

Log viewer:

```text
10:29:32 INFO  request started
10:29:33 INFO  payment request
10:29:35 ERROR connection pool exhausted
10:29:35 ERROR checkout failed
```

Features:

```text
Search
Filter level
Filter service
Copy
Expand
Jump to timestamp
```

---

# 74. Code Viewer

Features:

```text
Syntax highlighting
Line numbers
Search
Diff mode
Copy
GitHub link
```

Never render code as unformatted plain text.

---

# 75. Tool Call Viewer

For advanced users:

```text
Tool Call

Agent:
Log Agent

Tool:
search_logs

Arguments:

service = checkout-api
query = 500
range = last_30_minutes

Result:

1,204 matching logs

Duration:
842 ms
```

This demonstrates the agent/tool architecture.

---

# 76. Agent Run Details

```text
Agent:
Root Cause Agent

Run ID:
run_123

Status:
✓ Completed

Duration:
2.3s

LLM:
Gemini

Input tokens:
...

Output tokens:
...

Tools:
0

Evidence:
4

Result:
Root cause identified
```

This is useful for debugging and evaluation.

---

# 77. Evaluation UX — Benchmark Overview

```text
Evaluation Suite

Version: v0.8

Cases: 100

┌─────────────────────┐
│ Root Cause Accuracy │
│ 87%                 │
└─────────────────────┘

┌─────────────────────┐
│ Evidence Grounding  │
│ 93%                 │
└─────────────────────┘

┌─────────────────────┐
│ Tool Selection      │
│ 91%                 │
└─────────────────────┘
```

---

# 78. Evaluation Comparison

Allow:

```text
v0.7 vs v0.8
```

Show:

```text
Metric              v0.7    v0.8    Change
Root cause          84%     87%     +3%
Grounding           91%     93%     +2%
Tool selection      90%     91%     +1%
Latency             34s     31s     -3s
```

Do not label a version "better" automatically; present the measured changes.

---

# 79. Architecture Page

The public demo should include an architecture page.

Show:

```text
User
 ↓
Next.js
 ↓
FastAPI
 ↓
LangGraph
 ↓
Multi-Agent System
 ↓
MCP
 ↓
Logs / GitHub / Metrics
 ↓
RAG / Memory
 ↓
Evaluation
 ↓
Guardrails
```

Each component can be clicked to reveal a short explanation.

---

# 80. "How It Works" Page

A non-technical visitor should understand the system.

Example:

```text
1. Report an incident
2. Agents investigate different evidence sources
3. Evidence is correlated
4. AI proposes a root cause
5. AI prepares a fix
6. Human approves
7. Fix is tested
8. GitHub PR is created
```

---

# 81. Recruiter Demo Mode

The product should have a dedicated:

```text
Recruiter Demo
```

button.

It launches a preconfigured incident.

Suggested flow:

```text
Launch Demo
 ↓
Checkout Failure
 ↓
Start Investigation
 ↓
Watch Agents
 ↓
View Evidence
 ↓
View Root Cause
 ↓
Review Fix
 ↓
Approve
 ↓
Watch Tests
 ↓
View PR
 ↓
View Evaluation
```

Target demo duration:

```text
3–5 minutes
```

---

# 82. First-Time User Experience

First-time user sees:

```text
Welcome to TraceForge

TraceForge investigates software incidents
using AI agents.

[ Launch Guided Demo ]

or

[ Connect Your Project ]
```

The guided demo should explain the product while it runs.

---

# 83. Guided Demo

Use lightweight tooltips:

```text
This is the Supervisor Agent.
It coordinates specialized agents.

This is the Evidence panel.
Every major conclusion can be traced
back to collected evidence.

This approval step prevents autonomous
high-risk actions.
```

Do not create a long tutorial.

---

# 84. Dark Mode

Dark mode is the primary visual mode.

Recommended surface hierarchy:

```text
Page background
   ↓
Sidebar / Header
   ↓
Cards
   ↓
Nested panels
   ↓
Code / Log surfaces
```

Each level should have subtle separation.

---

# 85. Light Mode

Light mode is optional but should be supported if implemented.

Do not simply invert colors.

Maintain:

```text
Contrast
Borders
Semantic colors
Readable code
Readable logs
```

---

# 86. Visual Density

TraceForge is an engineering application.

Target:

```text
Medium-high information density
```

But use whitespace around major sections.

Avoid:

```text
Huge cards
Huge headings
Excessive empty space
```

---

# 87. Responsive Breakpoints

Suggested:

```text
Mobile:
< 640px

Tablet:
640px – 1024px

Desktop:
1024px – 1440px

Large desktop:
> 1440px
```

Use responsive layouts rather than fixed-width dashboards.

---

# 88. Accessibility States

For every status:

```text
✓ Completed
```

not just:

```text
green dot
```

For severity:

```text
🔴 HIGH
```

not just:

```text
red badge
```

For approval:

```text
⚠ Approval required
```

not just an amber border.

---

# 89. Performance

The investigation UI should feel responsive even while agents are running.

Use:

```text
Streaming events
Skeleton loading
Optimistic UI where safe
Pagination
Virtualized logs for large datasets
Lazy-loaded detail panels
```

Do not load thousands of logs into the browser at once.

---

# 90. Frontend Data Strategy

Use TanStack Query for server state.

Example:

```text
useQuery
  → incidents

useQuery
  → evidence

useQuery
  → report

SSE
  → live investigation events
```

The event stream should invalidate or update relevant cached queries.

---

# 91. UI State vs Server State

### UI state

```text
Open drawer
Selected tab
Modal visibility
Filter
Search input
```

### Server state

```text
Incident
Agent status
Evidence
Root cause
Approval
Test results
```

Do not mix them unnecessarily.

---

# 92. UI Security

Never assume hidden UI controls provide security.

For example:

```text
Hide "Approve" button
```

is not security.

The backend must independently verify:

```text
authenticated user
authorized role
incident ownership
approval permissions
action validity
```

---

# 93. Dangerous Action UX

For a high-risk operation:

```text
┌───────────────────────────────────────────────┐
│ ⚠ HIGH-RISK ACTION                           │
├───────────────────────────────────────────────┤
│                                               │
│ Proposed action:                              │
│ Modify production database                    │
│                                               │
│ This action is blocked by default.            │
│                                               │
│ Reason:                                       │
│ Production mutations require external         │
│ deployment controls.                          │
│                                               │
│ [ Close ]                                     │
└───────────────────────────────────────────────┘
```

Do not provide a misleading "Continue" button.

---

# 94. Design Tokens

Use centralized tokens.

Example:

```text
--background
--surface
--surface-elevated
--border
--text-primary
--text-secondary
--text-muted

--primary
--success
--warning
--danger
--info

--radius-sm
--radius-md
--radius-lg

--spacing-1
--spacing-2
--spacing-3
...
```

---

# 95. UI Technology

Recommended:

```text
Next.js
TypeScript
Tailwind CSS
shadcn/ui
TanStack Query
Lucide Icons
Recharts or equivalent chart library
Monaco Editor for code/diff where appropriate
```

Do not add a large UI framework on top of shadcn/ui unless there is a specific requirement.

---

# 96. Recommended Component Hierarchy

```text
AppShell
├── Sidebar
├── Header
└── MainContent

IncidentPage
├── IncidentHeader
├── StatusSummary
├── InvestigationTabs
│
├── InvestigationTimeline
│   └── TimelineItem
│
├── AgentPanel
│   └── AgentCard
│
├── EvidencePanel
│   └── EvidenceCard
│
├── RootCauseCard
├── HypothesisPanel
├── RemediationPanel
├── ApprovalDialog
├── SandboxResults
└── PullRequestCard
```

---

# 97. Frontend Folder Structure

```text
frontend/
├── app/
│   ├── page.tsx
│   ├── dashboard/
│   ├── incidents/
│   ├── projects/
│   ├── evaluations/
│   ├── agents/
│   ├── tools/
│   └── settings/
│
├── components/
│   ├── layout/
│   ├── dashboard/
│   ├── incident/
│   ├── investigation/
│   ├── evidence/
│   ├── agents/
│   ├── remediation/
│   ├── evaluation/
│   └── ui/
│
├── hooks/
│   ├── useIncident.ts
│   ├── useInvestigation.ts
│   └── useInvestigationEvents.ts
│
├── lib/
│   ├── api.ts
│   ├── sse.ts
│   └── utils.ts
│
└── types/
```

---

# 98. Core User Journey

The primary journey is:

```text
Landing
   ↓
Try Demo
   ↓
Select Incident
   ↓
Incident Created
   ↓
Investigation Running
   ↓
Agent Timeline
   ↓
Evidence
   ↓
Root Cause
   ↓
Remediation
   ↓
Approval
   ↓
Testing
   ↓
Pull Request
   ↓
Evaluation
```

---

# 99. UI Success Criteria

A first-time user should understand within 30 seconds:

1. What TraceForge does.
2. What an incident is.
3. What the agents are doing.
4. Where the evidence came from.
5. What the AI believes the root cause is.
6. What action it wants to take.
7. Where human approval is required.
8. Whether the fix passed testing.

---

# 100. Final UI Principle

TraceForge should visually communicate:

```text
NOT

User → Chatbot → Answer


BUT

User
 ↓
Incident
 ↓
AI Investigation
 ↓
Multiple Agents
 ↓
Evidence
 ↓
Root Cause
 ↓
Controlled Remediation
 ↓
Human Approval
 ↓
Verified Fix
```

The UI is successful when a recruiter can open the deployed product, run one incident, watch the agents work, inspect the evidence, review a proposed fix, see the safety boundary, and understand the engineering behind the system without needing to read the source code first.
