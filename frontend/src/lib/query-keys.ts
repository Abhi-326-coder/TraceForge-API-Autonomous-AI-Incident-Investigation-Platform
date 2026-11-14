export const queryKeys = {
  evaluations: { dashboard: () => ["evaluations", "dashboard"] as const },
  projects: {
    list: () => ["projects"] as const,
    detail: (projectId: number) => ["projects", projectId] as const,
  },
  incidents: {
    list: () => ["incidents"] as const,
    detail: (incidentId: number) => ["incidents", incidentId] as const,
    detailOrUnresolved: (incidentId: number | null) => incidentId === null
      ? ["incidents", "unresolved"] as const
      : ["incidents", incidentId] as const,
    investigations: (incidentId: number) => ["incidents", incidentId, "investigations"] as const,
    investigationsOrUnresolved: (incidentId: number | null) => incidentId === null
      ? ["incidents", "unresolved", "investigations"] as const
      : ["incidents", incidentId, "investigations"] as const,
    logs: (incidentId: number) => ["incidents", incidentId, "logs"] as const,
    logsOrUnresolved: (incidentId: number | null) => incidentId === null
      ? ["incidents", "unresolved", "logs"] as const
      : ["incidents", incidentId, "logs"] as const,
    metrics: (incidentId: number) => ["incidents", incidentId, "metrics"] as const,
    metricsOrUnresolved: (incidentId: number | null) => incidentId === null
      ? ["incidents", "unresolved", "metrics"] as const
      : ["incidents", incidentId, "metrics"] as const,
  },
  investigations: {
    evidence: (investigationId: number) => ["investigations", investigationId, "evidence"] as const,
  },
  patches: { detail: (patchId: number) => ["patches", patchId] as const },
} as const;
