import { apiClient } from "../api-client.ts";
import type { RootCause } from "@/types/investigation";

export type Incident = {
  id: number;
  external_id: string;
  title: string;
  description: string;
  service: string;
  severity: string;
  status: string;
  project_id: number;
  created_at: string;
};

export type Investigation = {
  id: number;
  incident_id: number;
  status: string;
  current_stage: string;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
};

export type CreateIncidentInput = {
  title: string;
  description: string;
  service: string;
  severity: string;
};

export type IncidentLog = {
  timestamp: string;
  service: string;
  level: string;
  message: string;
};

export type IncidentMetrics = {
  request_rate: number;
  error_rate: number;
  latency_ms: number;
  database_connections: number;
  database_connection_limit: number;
};

export type InvestigationRunResult = {
  investigation_id: number;
  task_id: string;
  status: string;
  message: string;
};

export function parseInvestigation(value: unknown): Investigation {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid investigation response.");
  const item = value as Record<string, unknown>;
  const isTimestamp = (field: unknown) => typeof field === "string";
  if (typeof item.id !== "number" || typeof item.incident_id !== "number" || typeof item.status !== "string" ||
    typeof item.current_stage !== "string" || !isTimestamp(item.created_at) ||
    (item.started_at !== null && !isTimestamp(item.started_at)) || (item.completed_at !== null && !isTimestamp(item.completed_at))) {
    throw new Error("Invalid investigation response.");
  }
  return item as unknown as Investigation;
}

export function parseRootCause(value: unknown): RootCause {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("Invalid root-cause response.");
  const item = value as Record<string, unknown>;
  const alternatives = item.alternative_causes;
  if (typeof item.root_cause !== "string" || typeof item.explanation !== "string" || typeof item.confidence !== "number" ||
    item.confidence < 0 || item.confidence > 1 || !Array.isArray(item.evidence_ids) || !item.evidence_ids.every((id) => typeof id === "number") ||
    !Array.isArray(alternatives) || !alternatives.every((alternative) => alternative && typeof alternative === "object" && typeof (alternative as Record<string, unknown>).cause === "string" && typeof (alternative as Record<string, unknown>).reason_not_primary === "string") || typeof item.uncertainty !== "string") {
    throw new Error("Invalid root-cause response.");
  }
  return item as unknown as RootCause;
}

export const incidentsApi = {
  list: () => apiClient.get<Incident[]>("/api/incidents"),
  create: (projectId: number, input: CreateIncidentInput) => apiClient.post<Incident>("/api/incidents", input, { query: { project_id: projectId } }),
  get: (incidentId: number) => apiClient.get<Incident>(`/api/incidents/${incidentId}`),
  getLogs: (incidentId: number) => apiClient.get<IncidentLog[]>(`/api/incidents/${incidentId}/logs`),
  getMetrics: (incidentId: number) => apiClient.get<IncidentMetrics>(`/api/incidents/${incidentId}/metrics`),
  listInvestigations: async (incidentId: number) => (await apiClient.get<unknown[]>(`/api/incidents/${incidentId}/investigations`)).map(parseInvestigation),
  startInvestigation: (incidentId: number) => apiClient.post<Investigation>(`/api/incidents/${incidentId}/investigate`),
  runInvestigation: (investigationId: number) => apiClient.post<InvestigationRunResult>(`/api/investigations/${investigationId}/run`),
  generateRootCause: async (incidentId: number) => parseRootCause(await apiClient.post<unknown>(`/api/incidents/${incidentId}/root-cause`)),
};
