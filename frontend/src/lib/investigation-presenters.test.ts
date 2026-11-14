import assert from "node:assert/strict";
import test from "node:test";
import { timelineEventDetails } from "./investigation-presenters.ts";

test("timeline mapping exposes backend stage and evidence references", () => {
  assert.deepEqual(timelineEventDetails({ event_type: "evidence_collected", investigation_id: 2, message: "Collected", timestamp: "2026-01-01T00:00:00Z", data: { stage: "collecting", evidence_ids: [3, "bad"], evidence_id: 5 } }), { stage: "collecting", evidenceIds: [3] });
  assert.deepEqual(timelineEventDetails({ event_type: "agent_started", investigation_id: 2, message: "Started", timestamp: "2026-01-01T00:00:00Z", data: { evidence_id: 5 } }), { stage: undefined, evidenceIds: [5] });
});
