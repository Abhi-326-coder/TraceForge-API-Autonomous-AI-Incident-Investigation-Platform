import type { CreatePatchInput } from "@/types/patch";
export type PatchFormErrors = Partial<Record<keyof CreatePatchInput, string>>;
export function validatePatch(input: CreatePatchInput): PatchFormErrors {
  const errors: PatchFormErrors = {};
  if (!Number.isInteger(input.investigation_id) || input.investigation_id <= 0) errors.investigation_id = "Enter a valid investigation ID.";
  if (!input.patch_summary.trim()) errors.patch_summary = "Enter a patch summary.";
  if (!input.diff.trim() || !input.diff.includes("---") || !input.diff.includes("+++")) errors.diff = "Provide a unified diff containing --- and +++ headers.";
  if (!input.changed_files.length || input.changed_files.some((path) => !path.trim())) errors.changed_files = "Enter at least one changed file path.";
  if (!input.tests_to_run.length || input.tests_to_run.some((test) => !test.trim())) errors.tests_to_run = "Enter at least one test to run.";
  if (!input.risks.length || input.risks.some((risk) => !risk.trim())) errors.risks = "Enter at least one risk.";
  if (!Object.keys(input.proposed_files).length || Object.entries(input.proposed_files).some(([path, content]) => !path.trim() || !content.trim())) errors.proposed_files = "Provide full content for every proposed file.";
  if (!errors.changed_files && !errors.proposed_files && input.changed_files.length !== Object.keys(input.proposed_files).length) errors.proposed_files = "Proposed files must match the changed file list.";
  return errors;
}
