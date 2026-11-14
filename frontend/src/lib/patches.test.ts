import assert from "node:assert/strict";
import test from "node:test";
import { parsePatch, patchesApi } from "./api/patches.ts";
import { queryKeys } from "./query-keys.ts";
const patch = { id: 7, investigation_id: 3, patch_summary: "Fix", diff: "--- a/a\n+++ b/a", changed_files: ["a"], tests_to_run: ["test"], risks: ["risk"], status: "PENDING", decision_note: null, decided_by: null, created_at: "2026-01-01T00:00:00Z", decided_at: null };
test("patch parser maps the durable review DTO", () => { assert.equal(parsePatch(patch).id, 7); assert.throws(() => parsePatch({ id: 7 })); assert.deepEqual(queryKeys.patches.detail(7), ["patches", 7]); });
test("patch decision uses the BFF endpoint and exact decision body", async () => { let url = ""; let body = ""; globalThis.fetch = async (input, init) => { url = String(input); body = String(init?.body); return new Response(JSON.stringify(patch), { headers: { "Content-Type": "application/json" } }); }; await patchesApi.decide(7, "APPROVED", "Reviewed"); assert.equal(url, "/api/backend/api/patches/7/decision"); assert.equal(body, '{"decision":"APPROVED","note":"Reviewed"}'); });
