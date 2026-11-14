import assert from "node:assert/strict";
import test from "node:test";

import { incidentsApi, parseInvestigation, parseRootCause } from "./api/incidents.ts";

const originalFetch = globalThis.fetch;

test("incidents API lists and creates through the same-origin BFF", async () => {
  const requests: Array<{ url: string; init: RequestInit | undefined }> = [];
  globalThis.fetch = async (input, init) => {
    requests.push({ url: String(input), init });
    return new Response(JSON.stringify([]), { headers: { "Content-Type": "application/json" } });
  };
  await incidentsApi.list();
  await incidentsApi.create(8, { title: "Checkout errors", description: "Requests fail", service: "checkout", severity: "HIGH" });
  assert.equal(requests[0]?.url, "/api/backend/api/incidents");
  assert.equal(requests[1]?.url, "/api/backend/api/incidents?project_id=8");
  assert.equal(requests[1]?.init?.method, "POST");
  globalThis.fetch = originalFetch;
});

test("investigation run uses the explicit run endpoint", async () => {
  let capturedUrl = "";
  globalThis.fetch = async (input) => {
    capturedUrl = String(input);
    return new Response(JSON.stringify({ investigation_id: 11, task_id: "mock-task", status: "QUEUED", message: "Queued" }), { headers: { "Content-Type": "application/json" } });
  };
  const result = await incidentsApi.runInvestigation(11);
  assert.equal(capturedUrl, "/api/backend/api/investigations/11/run");
  assert.equal(result.status, "QUEUED");
  globalThis.fetch = originalFetch;
});

test("investigation DTO parsing rejects incomplete backend responses", () => {
  assert.equal(parseInvestigation({ id: 1, incident_id: 2, status: "FAILED", current_stage: "failed", created_at: "2026-01-01T00:00:00Z", started_at: null, completed_at: null }).status, "FAILED");
  assert.throws(() => parseInvestigation({ id: 1 }));
});

test("root-cause response parsing keeps evidence traceability", () => {
  const rootCause = parseRootCause({ root_cause: "Pool exhaustion", explanation: "Connections reached the limit.", confidence: 0.8, evidence_ids: [4, 8], alternative_causes: [{ cause: "Slow queries", reason_not_primary: "No matching evidence" }], uncertainty: "Traffic contribution is unknown." });
  assert.deepEqual(rootCause.evidence_ids, [4, 8]);
  assert.throws(() => parseRootCause({ root_cause: "Missing fields" }));
});

test("root-cause generation posts only to the explicit incident action", async () => {
  let url = "";
  globalThis.fetch = async (input) => { url = String(input); return new Response(JSON.stringify({ root_cause: "Pool exhaustion", explanation: "Connections reached the limit.", confidence: 0.8, evidence_ids: [4], alternative_causes: [], uncertainty: "Unknown." }), { headers: { "Content-Type": "application/json" } }); };
  await incidentsApi.generateRootCause(12);
  assert.equal(url, "/api/backend/api/incidents/12/root-cause");
});
