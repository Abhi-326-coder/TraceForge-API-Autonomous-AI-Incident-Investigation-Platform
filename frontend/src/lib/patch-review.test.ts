import assert from "node:assert/strict";
import test from "node:test";
import { classifyPatchDiffLine, patchReviewSummary } from "./patch-review.ts";
import { parsePatch } from "./api/patches.ts";

const basePatch = {
  id: 19, investigation_id: 5, patch_summary: "Handle timeout", diff: "@@ -1 +1 @@\n-old\n+new",
  changed_files: ["src/api.ts", "src/client.ts"], tests_to_run: ["pytest"], risks: ["Retry behavior"],
  status: "PENDING", decision_note: null, decided_by: null, created_at: "2026-11-17T10:00:00Z", decided_at: null,
};

test("review summary exposes file count and pending decision availability", () => {
  const patch = parsePatch(basePatch);
  assert.equal(patch.patch_summary, "Handle timeout");
  assert.deepEqual(patch.changed_files, ["src/api.ts", "src/client.ts"]);
  assert.deepEqual(patch.tests_to_run, ["pytest"]);
  assert.deepEqual(patch.risks, ["Retry behavior"]);
  assert.deepEqual(patchReviewSummary(patch), { fileCount: 2, hasDecisionControls: true, proposedFilesAvailable: false, assumptionsAvailable: false });
});

test("diff lines classify additions, deletions, headers, and context", () => {
  assert.equal(classifyPatchDiffLine("+new code"), "addition");
  assert.equal(classifyPatchDiffLine("-old code"), "deletion");
  assert.equal(classifyPatchDiffLine("@@ -1 +1 @@"), "header");
  assert.equal(classifyPatchDiffLine(" unchanged  "), "context");
});

test("review accepts complete proposed files only when API provides them and hides controls after decision", () => {
  const withFiles = parsePatch({ ...basePatch, proposed_files: { "src/api.ts": "complete source" }, assumptions: ["Network is eventually available"] });
  assert.equal(withFiles.proposed_files?.["src/api.ts"], "complete source");
  assert.equal(patchReviewSummary(withFiles).proposedFilesAvailable, true);
  assert.equal(patchReviewSummary(withFiles).assumptionsAvailable, true);
  const decided = parsePatch({ ...basePatch, status: "APPROVED", decision_note: "Reviewed", decided_by: "7", decided_at: basePatch.created_at });
  assert.equal(patchReviewSummary(decided).hasDecisionControls, false);
});
