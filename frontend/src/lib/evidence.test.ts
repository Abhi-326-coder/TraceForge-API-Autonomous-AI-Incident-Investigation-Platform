import assert from "node:assert/strict";
import test from "node:test";
import { evidenceApi } from "./api/evidence.ts";
import { queryKeys } from "./query-keys.ts";

test("evidence uses its investigation-scoped BFF endpoint and query key", async () => {
  let url = "";
  globalThis.fetch = async (input) => { url = String(input); return new Response(JSON.stringify([]), { headers: { "Content-Type": "application/json" } }); };
  await evidenceApi.list(41);
  assert.equal(url, "/api/backend/api/investigations/41/evidence");
  assert.deepEqual(queryKeys.investigations.evidence(41), ["investigations", 41, "evidence"]);
});
