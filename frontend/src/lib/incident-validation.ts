import type { CreateIncidentInput } from "./api/incidents.ts";

export type IncidentFormInput = CreateIncidentInput & { projectId: number | null };
export type IncidentFormErrors = Partial<Record<keyof IncidentFormInput, string>>;

export function validateIncident(input: IncidentFormInput): IncidentFormErrors {
  const errors: IncidentFormErrors = {};
  if (!input.projectId) errors.projectId = "Select a project.";
  if (!input.title.trim()) errors.title = "Enter an incident title.";
  if (!input.description.trim()) errors.description = "Enter an incident description.";
  if (!input.service.trim()) errors.service = "Enter the affected service.";
  if (!input.severity.trim()) errors.severity = "Select a severity.";
  return errors;
}
