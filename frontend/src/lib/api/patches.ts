import { apiClient } from "../api-client.ts";
import type { CreatePatchInput, Patch, PatchDecision } from "@/types/patch";

export function parsePatch(value: unknown): Patch {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid patch response.");
  const item = value as Record<string, unknown>;
  const strings = (field: unknown) => Array.isArray(field) && field.every((entry) => typeof entry === "string");
  if (typeof item.id !== "number" || typeof item.investigation_id !== "number" || typeof item.patch_summary !== "string" || typeof item.diff !== "string" || !strings(item.changed_files) || !strings(item.tests_to_run) || !strings(item.risks) || typeof item.status !== "string" || (item.decision_note !== null && typeof item.decision_note !== "string") || (item.decided_by !== null && typeof item.decided_by !== "string") || typeof item.created_at !== "string" || (item.decided_at !== null && typeof item.decided_at !== "string")) throw new Error("Invalid patch response.");
  if (item.assumptions !== undefined && !strings(item.assumptions)) throw new Error("Invalid patch response.");
  if (item.proposed_files !== undefined && (!item.proposed_files || typeof item.proposed_files !== "object" || Array.isArray(item.proposed_files) || !Object.values(item.proposed_files).every((content) => typeof content === "string"))) throw new Error("Invalid patch response.");
  return item as unknown as Patch;
}

export const patchesApi = {
  generate: async (investigationId: number) => parsePatch(await apiClient.post<unknown>("/api/patches/generate", { investigation_id: investigationId })),
  create: async (input: CreatePatchInput) => parsePatch(await apiClient.post<unknown>("/api/patches", input)),
  get: async (patchId: number) => parsePatch(await apiClient.get<unknown>(`/api/patches/${patchId}`)),
  decide: async (patchId: number, decision: PatchDecision, note?: string) => parsePatch(await apiClient.post<unknown>(`/api/patches/${patchId}/decision`, { decision, note: note ?? "" })),
  listForInvestigation: async (investigationId: number) => (await apiClient.get<unknown[]>(`/api/investigations/${investigationId}/patches`)).map(parsePatch),
  createBranch: (patchId: number) => apiClient.post<{branch_name: string; sha: string; url: string; simulated?: boolean; message?: string}>(`/api/patches/${patchId}/branch`, { owner: "configured-project", repo: "configured-project", base_branch: "configured-project" }),
  createPullRequest: (patchId: number) => apiClient.post<{commit_sha: string; branch: string; pr_number: number | null; pr_url: string | null; pr_state: string; draft: boolean; simulated?: boolean; message?: string}>(`/api/patches/${patchId}/pull-request`, { owner: "configured-project", repo: "configured-project", base_branch: "configured-project" }),
};
