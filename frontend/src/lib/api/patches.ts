import { apiClient } from "../api-client.ts";
import type { CreatePatchInput, Patch, PatchDecision } from "@/types/patch";

export function parsePatch(value: unknown): Patch {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid patch response.");
  const item = value as Record<string, unknown>;
  const strings = (field: unknown) => Array.isArray(field) && field.every((entry) => typeof entry === "string");
  if (typeof item.id !== "number" || typeof item.investigation_id !== "number" || typeof item.patch_summary !== "string" || typeof item.diff !== "string" || !strings(item.changed_files) || !strings(item.tests_to_run) || !strings(item.risks) || typeof item.status !== "string" || (item.decision_note !== null && typeof item.decision_note !== "string") || (item.decided_by !== null && typeof item.decided_by !== "string") || typeof item.created_at !== "string" || (item.decided_at !== null && typeof item.decided_at !== "string")) throw new Error("Invalid patch response.");
  return item as unknown as Patch;
}

export const patchesApi = {
  create: async (input: CreatePatchInput) => parsePatch(await apiClient.post<unknown>("/api/patches", input)),
  get: async (patchId: number) => parsePatch(await apiClient.get<unknown>(`/api/patches/${patchId}`)),
  decide: async (patchId: number, decision: PatchDecision, note?: string) => parsePatch(await apiClient.post<unknown>(`/api/patches/${patchId}/decision`, { decision, note: note ?? "" })),
};
