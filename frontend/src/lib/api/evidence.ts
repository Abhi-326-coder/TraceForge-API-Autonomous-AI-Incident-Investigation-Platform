import { apiClient } from "../api-client.ts";
import type { Evidence } from "@/types/investigation";

export function parseEvidence(value: unknown): Evidence {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid evidence response.");
  const item = value as Record<string, unknown>;
  if (typeof item.id !== "number" || typeof item.investigation_id !== "number" || typeof item.source_type !== "string" ||
    typeof item.provider !== "string" || typeof item.title !== "string" || typeof item.content !== "string" ||
    typeof item.created_at !== "string" || (item.source_reference !== null && typeof item.source_reference !== "string")) {
    throw new Error("Invalid evidence response.");
  }
  return item as unknown as Evidence;
}

export const evidenceApi = {
  list: async (investigationId: number) => (await apiClient.get<unknown[]>(`/api/investigations/${investigationId}/evidence`)).map(parseEvidence),
};
