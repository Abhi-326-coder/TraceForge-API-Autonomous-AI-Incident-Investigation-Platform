import type { Patch } from "@/types/patch";

export function patchReviewSummary(patch: Patch) {
  return {
    fileCount: patch.changed_files.length,
    hasDecisionControls: patch.status === "PENDING",
    proposedFilesAvailable: Boolean(patch.proposed_files && Object.keys(patch.proposed_files).length),
    assumptionsAvailable: Boolean(patch.assumptions?.length),
  };
}

export function classifyPatchDiffLine(line: string): "addition" | "deletion" | "header" | "context" {
  if (line.startsWith("+++ ") || line.startsWith("--- ") || line.startsWith("@@")) return "header";
  if (line.startsWith("+")) return "addition";
  if (line.startsWith("-")) return "deletion";
  return "context";
}
