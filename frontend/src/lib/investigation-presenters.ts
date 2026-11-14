import type { InvestigationEvent } from "@/types/investigation";

export function timelineEventDetails(event: InvestigationEvent) {
  const stage = typeof event.data.stage === "string" ? event.data.stage : undefined;
  const evidenceIds = Array.isArray(event.data.evidence_ids)
    ? event.data.evidence_ids.filter((id): id is number => typeof id === "number")
    : typeof event.data.evidence_id === "number" ? [event.data.evidence_id] : [];
  return { stage, evidenceIds };
}
