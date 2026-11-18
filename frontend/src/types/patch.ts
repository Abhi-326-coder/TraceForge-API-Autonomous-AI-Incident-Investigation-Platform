export type PatchStatus = "PENDING" | "APPROVED" | "REJECTED" | string;
export type Patch = {
  id: number; investigation_id: number; patch_summary: string; diff: string;
  changed_files: string[]; tests_to_run: string[]; risks: string[]; status: PatchStatus;
  proposed_files?: Record<string, string>;
  assumptions?: string[];
  decision_note: string | null; decided_by: string | null; created_at: string; decided_at: string | null;
  github_branch?: string | null; github_branch_sha?: string | null; github_branch_url?: string | null;
  github_commit_sha?: string | null; github_pr_number?: number | null; github_pr_url?: string | null; github_pr_state?: string | null;
};
export type CreatePatchInput = { investigation_id: number; patch_summary: string; diff: string; changed_files: string[]; tests_to_run: string[]; risks: string[]; proposed_files: Record<string, string> };
export type PatchDecision = "APPROVED" | "REJECTED";
