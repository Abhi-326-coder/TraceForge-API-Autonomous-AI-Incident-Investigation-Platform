import assert from "node:assert/strict";
import test from "node:test";
import { validatePatch } from "./patch-validation.ts";
const valid = { investigation_id: 3, patch_summary: "Fix pool", diff: "--- a/db.ts\n+++ b/db.ts\n", changed_files: ["db.ts"], tests_to_run: ["npm test"], risks: ["Regression"], proposed_files: { "db.ts": "new content" } };
test("patch validation accepts complete user-supplied remediation", () => assert.deepEqual(validatePatch(valid), {}));
test("patch validation rejects malformed and incomplete remediation", () => { const errors = validatePatch({ ...valid, diff: "plain text", proposed_files: {} }); assert.ok(errors.diff); assert.ok(errors.proposed_files); });
