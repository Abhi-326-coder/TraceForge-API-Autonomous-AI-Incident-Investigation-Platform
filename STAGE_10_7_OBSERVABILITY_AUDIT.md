# Stage 10.7 — Observability Audit

**Scope:** Inspection only, based on the repository at the time of review. No application code, tests, migrations, configuration, or running service state was changed. No live provider calls were made.

## Current observability architecture

TraceForge has four separate operational data paths:

1. **PostgreSQL application state** holds each investigation's current status, stage, timestamps, worker ID, lease token, heartbeat and expiry, and sanitized failure category/message/terminal flag. The transactionally created outbox row records an investigation dispatch intent and its current delivery status/attempt count.
2. **Redis investigation event stream** stores graph progress events for 24 hours and publishes them to live SSE subscribers. Deterministic event IDs make graph node event appends idempotent within that Redis retention window.
3. **Process logs** are mostly Python/Celery defaults. Explicit application logging is sparse; the outbox dispatcher and investigation enqueue route are the main named logger users. Some modules use `print`.
4. **OpenTelemetry tracing** is configured in `app/observability/tracing.py`, with FastAPI and SQLAlchemy instrumentation in `main.py`; the investigation worker creates spans. The exporter is console in debug and OTLP gRPC otherwise.

There is no Prometheus exposition endpoint or durable metrics backend in the inspected backend. The project also has “metrics” providers/MCP tools for inspecting application/service incident metrics; those are investigation inputs, not platform operational telemetry.

## Existing logs, events, metrics, and health checks

### Investigation lifecycle and retries

- `Investigation` records `QUEUED`, `RUNNING`, `COMPLETED`, and `FAILED` in the asynchronous worker path. `claim_investigation` atomically claims queued work or expired running work, creates a fresh UUID lease token, and updates worker/heartbeat/expiry fields. Completion and failure are fenced by worker ID, token, status, and unexpired lease. Recovery returns invalid/expired `RUNNING` rows to `QUEUED`, clears stale ownership metadata, and ensures a durable dispatch intent.
- `current_stage` exists in the database and response schema, but worker claims and graph nodes do not update it. The worker does not persist an execution-attempt number. The Celery request ID is passed as `worker_id`, so this is a task ID, not a stable process/host identity.
- The failure classifier maps provider/network/configuration/input/unknown errors to a category, safe message, and retryability. `failure_category`, `failure_message`, and `failure_is_terminal` are persisted on `FAILED`; the message is deliberately allowlisted. Retry delay is exponential with jitter and capped at 60 seconds; Celery permits two retries. Before retry, the failed row is returned to `QUEUED`, clearing the failure fields. Thus retry history and prior failure classifications are lost from current investigation state.
- Heartbeat renews every 30 seconds against a 120-second lease. On renewal failure or exception, the heartbeat thread sets `lost_lease`, but does not log why. The next worker check turns this into a generic runtime failure; fencing prevents a stale worker from committing completion/failure or checkpoint/evidence side effects.
- There is also synchronous investigation service code using `INVESTIGATING`; this is a legacy/alternate path and differs from the queued Celery lifecycle. Current status vocabulary should be confirmed before consumers assume only four values.

### Structured logging and tracing

- Explicit logs: enqueue errors include the investigation ID and stack trace; outbox dispatch exceptions use `logger.exception` with outbox ID and event type. Neither includes a consistent set of incident/task/worker/attempt/stage fields.
- Investigation worker spans include `traceforge.investigation_id`, status on successful completion, and LangGraph thread ID. There are no explicit span attributes for incident ID, task/worker ID, attempt, stage, retry classification, lease state, or recovery outcome. Worker tasks and Beat tasks are not explicitly instrumented with Celery instrumentation in the inspected code.
- `configure_tracing` exports spans to console in debug and to an OTLP-compatible collector otherwise. No collector endpoint is apparent in the inspected Compose file. `get_tracer` uses a cached provider; no metrics provider/exporter is configured.
- Graph nodes publish progress events, not structured application logs. A Gemini agent uses `print`; sandbox runner prints source paths and file contents; evaluation runner prints. These are potential content disclosure paths if those flows receive customer or repository data.
- The event stream includes a supervisor plan, evidence ID, root cause text, and confidence. These are not logs, but are exposed through an authenticated SSE route to users authorized for the investigation. Event `data` is open-ended, so future contributors could accidentally include prompt or provider content.
- Investigation exceptions are re-raised in the worker and task code. The task replaces the exception passed to Celery retry with a safe message and strips chaining on terminal task errors, while the worker records only the safe classifier message. However, generic Celery/runtime stderr logging may still print exceptions or tracebacks from the worker exception path; there is no repository-wide redaction filter. Outbox `logger.exception` intentionally captures the underlying exception and traceback, which could leak details if broker/client exception strings contain URLs, payloads, or credentials.

### Persisted and streamed events

- Graph lifecycle events include supervisor started/completed; agent started/completed for log agent; evidence collected; root cause started/completed; investigation completed. Metrics/code nodes emit “not implemented” as agent-completed events. These are in Redis, not a durable relational event table.
- Redis append and event-ID set expire after 24 hours. Event IDs are deterministic from investigation ID, agent, and event type, so replayed same-type node events collapse to one entry even if a later logical attempt should be distinguished. IDs are not added to trace spans or log records.
- Event timestamps are created in application code with UTC-aware `datetime.now(timezone.utc)`. List order is Redis append order; concurrent publishers and replay can make that differ from logical execution ordering. There is no durable sequence number, retry/recovery/lease event, task correlation, or timestamp monotonicity guarantee. SSE polls the full event list every 500 ms and uses a local list offset; reconnect replay behavior is basic and retention-limited.
- Outbox status is durable but is dispatch infrastructure state, not an investigation lifecycle event. Recovery and outbox retries are not emitted as correlated lifecycle events.

### Metrics

- `AgentMetricsService` keeps agent/tool durations and outcome counts, plus root-cause/approval quality flags, in process memory. It is not durable, multi-worker aggregated, or exposed by an authenticated route in inspected files.
- `measure_duration` is a generic timing helper and `metrics_helpers.py` only offers a context manager callback. These do not constitute exported platform metrics.
- No platform counters/histograms/gauges were found for queue delay, investigation duration, retry/failure rates, recovery, outbox age/failures, worker heartbeat, or expired leases.

### Health and readiness

- `GET /health` is unauthenticated and always returns healthy; it is a process liveness check only. Docker Compose uses it as the API healthcheck.
- `GET /health/redis` pings Redis and returns 503 on error. It reports Redis reachability only, not Celery consumption or Beat scheduling.
- PostgreSQL, Celery worker, Beat, and PostgreSQL checkpoint readiness are not checked by API health endpoints. Compose checks PostgreSQL and Redis containers separately, and API dependency startup, but worker and Beat have no healthchecks. Worker/Beat start after API is healthy, not after their own readiness has been observed.
- The graph runtime opens a PostgreSQL checkpoint saver and calls `setup()` during execution. This demonstrates runtime setup, not an independently surfaced checkpoint readiness check.

### Operational diagnosis today

- An authorized user can list investigations and see status, current stage, and basic timestamps. Failure details, retry count/history, worker ID, heartbeat, lease expiry, and failure category are absent from `InvestigationResponse`.
- An engineer with database access can inspect lease timestamps, outbox state/attempts and sanitized terminal failure fields. There is no authenticated operator endpoint for these details.
- “Stuck” requires manual comparison of status and lease expiry/heartbeat. A slow but heartbeating worker cannot be distinguished by current stage/progress; an expired lease is only visible by querying the database and correlating with the periodic recovery task.
- Outbox rows have an `attempts` count, but failures return to `PENDING` without a recorded last error, next retry time, or terminal/dead-letter state. No poison event can be singled out from normal transient failures using an API; unsupported event types or malformed payloads can cycle indefinitely.

## Missing diagnostic capabilities

1. No durable attempt/retry history, retry reason, delay, task ID, worker process identity, or recovery/checkpoint-resume record.
2. Stage is not updated during graph execution, so persisted “current stage” is stale/default for asynchronous work.
3. No shared structured logging context across request, Celery, graph, heartbeat, recovery, and outbox; correlation IDs do not bridge database records, Redis events, logs, and spans.
4. Lease-loss cause (expired, token replaced, DB/Redis failure) is not recorded distinctly. Heartbeat catches every exception and only flags lost lease.
5. Redis events are ephemeral and omit retries, terminal failure, recovery, checkpoint resume, and lease loss. Deterministic IDs omit attempt identity, and no sequence field supports ordering.
6. No exported platform metrics or alertable operational counters/histograms/gauges.
7. Health checks do not distinguish liveness from dependency readiness or worker/Beat/checkpointer availability.
8. No authenticated, tenant-safe operational diagnostics for stuck jobs, lease status, failure classification, retry history, checkpoint state, or outbox poison events.
9. Outbox failures are logged but have no durable last failure metadata or bounded retry/parking policy; retry attempts are visible only as an increasing counter.
10. Logs are neither consistently structured nor centrally redacted. Trace exporter configuration and exception reporting need explicit privacy review.

## Sensitive-data and logging risks

- The failure classifier and investigation task correctly use safe messages for persisted failure state and Celery retry exceptions. Preserve this behavior; never persist raw provider exception text as a failure message.
- `logger.exception` in outbox dispatch records traceback and exception text. Review broker/client exceptions for embedded connection strings, credentials, event payloads, or endpoint data; add field allowlisting/redaction before expanding logging.
- `sandbox/runner.py` prints workspace paths, source file paths, and file contents. This is a direct source-code disclosure risk in collected container logs. Remove content logging or replace it with safe counts/identifiers before enabling centralized retention.
- `gemini_log_agent.py` prints response-related output; inspect and constrain its exact content before production log aggregation. Treat prompts, incident descriptions, evidence, source code, provider responses, auth headers/tokens, lease tokens, and full connection URLs as prohibited log/span attributes.
- Graph event payloads deliberately include plan/root cause data and future event `data` is unrestricted. Keep the authenticated tenant ownership check on SSE and define event schemas/allowlists that exclude prompt text, raw logs, provider response bodies, secrets, and source contents.
- Debug console tracing may expose captured request/SQL attributes depending on instrumentation configuration. Validate instrumentation capture settings and apply the same data classification/redaction policy to traces as logs.
- Never log the lease token. It is a fencing credential. Worker/task IDs and investigation/incident IDs are useful correlation fields but should be access-controlled in shared telemetry.

## Recommended structured logging schema

Emit one JSON object per operational event using stable, low-cardinality field names. Suggested common fields:

```json
{
  "timestamp": "RFC3339 UTC",
  "level": "INFO",
  "service.name": "traceforge-worker",
  "service.version": "...",
  "deployment.environment": "...",
  "event.name": "investigation.lease.claimed",
  "trace_id": "...",
  "span_id": "...",
  "request_id": "...",
  "investigation.id": "...",
  "incident.id": "...",
  "celery.task_id": "...",
  "worker.id": "stable process identity",
  "attempt.number": 1,
  "retry.classification": "PROVIDER_TIMEOUT",
  "investigation.status": "RUNNING",
  "investigation.stage": "root_cause",
  "lease.expires_at": "RFC3339 UTC",
  "outbox.event_id": "...",
  "outbox.event_type": "INVESTIGATION_REQUESTED",
  "error.type": "TimeoutError",
  "error.category": "PROVIDER_TIMEOUT",
  "error.safe_message": "The AI provider request timed out."
}
```

Populate only fields relevant to an event. Use the current attempt/task context rather than infer it from mutable database state. Do not include lease tokens, prompts, incident text, evidence, source contents, raw provider responses, credentials, or unbounded exception strings. For unexpected exceptions, keep a restricted traceback reference/fingerprint in protected logs, with a redacted traceback policy; expose only a safe category/message to users. Add explicit event names for claim, stage start/finish, retry scheduled, checkpoint resumed, lease heartbeat lost, recovery requeued, completion/failure, and outbox publish/retry/park.

## Recommended metrics and labels

Use the existing observability stack/dependencies where possible; first decide whether the configured OTLP path will support metrics or whether a simple existing-stack scrape/export path is intended. Avoid high-cardinality identifiers as metric labels.

| Metric | Type | Suggested bounded labels |
|---|---|---|
| Investigation transitions | Counter | `from_status`, `to_status`, `reason` |
| Investigation execution duration | Histogram | `outcome`, `stage` |
| Queue delay (`started_at - created_at`) | Histogram | `priority`/`severity` only if bounded |
| Retry attempts | Counter | `classification`, `retryable` |
| Investigation failures | Counter | `category`, `terminal` |
| Recovery actions | Counter | `reason`, `action` |
| Active investigations | Gauge | `status`, optionally bounded `stage` |
| Lease heartbeat age | Gauge/histogram | worker pool/queue, not worker ID |
| Expired leases observed/recovered | Counter | `reason` |
| Outbox pending age | Histogram/gauge | `event_type`, `status` |
| Outbox dispatch outcomes | Counter | `event_type`, `outcome` |
| Outbox attempts / poison events | Histogram/gauge | `event_type`, `status` |
| Dependency checks | Gauge/counter | `dependency`, `result` |

Do not label by investigation ID, incident ID, task ID, worker ID, raw exception, customer/project, or arbitrary provider error text. Keep those in access-controlled logs/traces instead.

## Recommended authenticated diagnostic API capabilities

Add an operator-oriented diagnostics surface, separate from ordinary user status and protected by explicit admin/operations authorization. All investigation lookups must retain tenant scoping unless a distinct audited cross-tenant operator role is used.

- Investigation detail: lifecycle timestamps, current stage, attempt number, retry history with safe categories/messages, terminal flag, last task ID, worker identity, heartbeat age, and lease expiry/expired boolean. Never return lease token.
- Investigation timeline: ordered lifecycle events with durable sequence/time, actor/source, attempt, safe metadata, recovery and checkpoint resume markers.
- Stuck-work query: queued age, running age, current stage duration, heartbeat age, lease expiry, and last progress; filterable by bounded status/category/time criteria and paginated.
- Outbox diagnostics: event ID/type/aggregate, status, attempts, age, lock age, last safe failure category/time, and parked/dead-letter indicator, plus controlled re-drive only in a later operational-action scope with audit/idempotency protections.
- Dependency readiness: DB, Redis, checkpoint store, worker queue/consumer and Beat heartbeat/schedule freshness. Keep unauthenticated liveness minimal and do not disclose dependency internals publicly.
- Audit every operator read/action, rate limit, return safe messages, and redact credentials, prompts, provider payloads, lease tokens, and tenant data not needed by the caller.

## Prioritized implementation plan

1. **Privacy and correlation foundation:** remove/replace content-bearing `print` calls; establish JSON logging and context propagation across API/Celery/graph/recovery/outbox; add redaction tests. Preserve sanitized failure messages and never expose lease tokens.
2. **Lifecycle observability:** persist attempt count and append-only attempt/transition history; update `current_stage` at graph node boundaries; record retries, checkpoint resume, lease loss, recovery, and terminal failures with monotonic sequence and UTC timestamps. Keep lease-token fencing and evidence/event idempotency unchanged.
3. **Outbox diagnostics and poison handling:** persist safe last failure metadata and retry timing; define bounded attempts/backoff and a parked state with audited/manual re-drive; retain outbox idempotency keys and transactional creation.
4. **Platform metrics and traces:** export queue delay, duration, retries/failures, recovery, lease and outbox signals with bounded labels; propagate trace context through Celery tasks and add safe attributes. Keep identifiers out of metric labels.
5. **Health and authenticated diagnostics:** separate liveness/readiness; check DB, Redis, checkpoint store and Celery worker/Beat freshness; deliver tenant-safe operator endpoints for timeline, stuck work, retry/failure, and outbox state.
6. **Verification and operations:** add unit/integration tests for structured field presence/redaction, transition and retry history, event ordering/idempotency, lease-loss/recovery, readiness failures, authorization/tenant isolation, outbox poison parking, and metric label cardinality. Add runbooks/alerts for expired leases, oldest queue age, oldest pending outbox age, retry exhaustion, and stale worker/Beat heartbeats.

## Relevant files and tests

**Core implementation:**

- `backend/app/db/models.py` — investigation, audit event, and outbox state fields.
- `backend/app/services/investigation_state_service.py` — claim/heartbeat/complete/fail/requeue/recovery transitions and fencing.
- `backend/app/services/investigation_worker_service.py` — worker execution, checkpoint resume, completion/failure handling, spans.
- `backend/app/services/investigation_retry.py`, `backend/app/tasks/investigation_tasks.py` — safe failure classification and Celery retries.
- `backend/app/services/worker_heartbeat_service.py` — lease renewal and silent lost-lease flag.
- `backend/app/graph/nodes.py`, `backend/app/graph/runtime.py`, `backend/app/graph/checkpointer.py` — graph events, node progress, lease-fenced checkpoints.
- `backend/app/services/event_service.py`, `backend/app/schemas/event.py`, `backend/app/routes/investigations.py` — Redis event retention, event schema, authenticated SSE.
- `backend/app/services/outbox_dispatcher_service.py`, `backend/app/tasks/outbox_tasks.py`, `backend/app/tasks/recovery_tasks.py` — dispatch/recovery behavior.
- `backend/app/observability/tracing.py`, `backend/app/main.py`, `backend/app/services/agent_metrics_service.py`, `backend/app/services/metrics_helpers.py` — traces, health endpoints, in-memory agent metrics.
- `backend/app/routes/investigation_jobs.py`, `backend/app/schemas/investigation.py`, `backend/app/worker.py`, `docker-compose.yml` — enqueue response, user status fields, Celery schedule and container health checks.
- `backend/app/sandbox/runner.py`, `backend/app/agents/gemini_log_agent.py` — content-bearing print/log review.

**Existing tests relevant to preserving guarantees:**

- `backend/tests/test_investigation_state_service.py`
- `backend/tests/test_investigation_retry_policy.py`
- `backend/tests/test_investigation_jobs.py`
- `backend/tests/test_investigation_recovery.py`
- `backend/tests/test_investigation_checkpoint_consistency.py`
- `backend/tests/test_event_service.py`
- `backend/tests/test_event_idempotency.py`
- `backend/tests/test_event_idempotency.py` and `backend/tests/test_evidence_idempotency.py`
- `backend/tests/test_outbox_service.py`, `backend/tests/test_outbox_dispatcher_service.py`
- `backend/tests/test_tracing.py`
- `backend/tests/test_authorization.py`, `backend/tests/test_tenant_security.py`

## Inspection checks and results

- Enumerated backend Python files, tests, Compose configuration, and project docs; searched observability, lifecycle, retry, lease, recovery, event, health, and outbox references.
- Read the implementation paths and targeted tests listed above. Confirmed existing tests explicitly cover lease-token fencing, checkpoint resume consistency, event idempotency, retry sanitization, outbox dispatch/recovery, and tenant authorization patterns.
- Did not execute tests, query a live database/Redis instance, inspect or print environment credentials, call Gemini/GitHub, run migrations, or mutate investigation/outbox/checkpoint state. No test results are claimed; recommendations identify the additional tests needed.

## To start the project without the docker Run these command:

# Terminal 1: PostgreSQL and Redis
docker compose up -d postgres redis
docker compose ps

Do not use down -v or remove volumes. After verifying the schema is compatible, start the backend:

# Terminal 2: Backend API
cd backend
$env:PYTHONPATH = "app"
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000

Start the worker separately so queued jobs can run in non-demo mode:

# Terminal 3: Celery worker
cd backend
$env:PYTHONPATH = "app"
.\.venv\Scripts\celery.exe -A app.worker:celery_app worker --loglevel=info

# Terminal 4: Celery beat
cd backend
$env:PYTHONPATH = "app"
.\.venv\Scripts\celery.exe -A app.worker:celery_app beat --loglevel=info

# Terminal 5: Frontend
cd frontend
npm run dev