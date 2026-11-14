import type { CreateProjectInput } from "./api/projects.ts";

export type ProjectFormErrors = Partial<Record<keyof CreateProjectInput, string>>;

export function validateProject(input: CreateProjectInput): ProjectFormErrors {
  if (!input.name.trim()) return { name: "Enter a project name." };
  return {};
}
