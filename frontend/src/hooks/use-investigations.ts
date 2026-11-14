"use client";

import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import { incidentsApi, type CreateIncidentInput } from "../lib/api/incidents.ts";
import { evidenceApi } from "../lib/api/evidence.ts";
import { patchesApi } from "../lib/api/patches.ts";
import type { CreatePatchInput, PatchDecision } from "../types/patch.ts";
import { queryKeys } from "../lib/query-keys.ts";

export function useIncident(incidentId: number | null) {
  return useQuery({
    queryKey: queryKeys.incidents.detailOrUnresolved(incidentId),
    queryFn: () => incidentsApi.get(incidentId!),
    enabled: incidentId !== null,
  });
}

export function useIncidents() {
  return useQuery({ queryKey: queryKeys.incidents.list(), queryFn: incidentsApi.list });
}

export function useIncidentLogs(incidentId: number | null) {
  return useQuery({
    queryKey: queryKeys.incidents.logsOrUnresolved(incidentId),
    queryFn: () => incidentsApi.getLogs(incidentId!),
    enabled: incidentId !== null,
  });
}

export function useIncidentMetrics(incidentId: number | null) {
  return useQuery({
    queryKey: queryKeys.incidents.metricsOrUnresolved(incidentId),
    queryFn: () => incidentsApi.getMetrics(incidentId!),
    enabled: incidentId !== null,
  });
}

export function useIncidentInvestigations(incidentId: number | null) {
  return useQuery({
    queryKey: queryKeys.incidents.investigationsOrUnresolved(incidentId),
    queryFn: () => incidentsApi.listInvestigations(incidentId!),
    enabled: incidentId !== null,
  });
}

export function useInvestigationEvidence(investigationId: number | null) {
  return useQuery({
    queryKey: investigationId === null ? ["investigations", "unresolved", "evidence"] : queryKeys.investigations.evidence(investigationId),
    queryFn: () => evidenceApi.list(investigationId!),
    enabled: investigationId !== null,
  });
}

export function startInvestigationMutationOptions(incidentId: number, queryClient: Pick<QueryClient, "invalidateQueries">) {
  return {
    mutationFn: () => incidentsApi.startInvestigation(incidentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.incidents.investigations(incidentId) }),
  };
}

export function useStartInvestigationMutation(incidentId: number) {
  const queryClient = useQueryClient();
  return useMutation(startInvestigationMutationOptions(incidentId, queryClient));
}

export function createIncidentMutationOptions(queryClient: Pick<QueryClient, "invalidateQueries">) {
  return {
    mutationFn: ({ projectId, input }: { projectId: number; input: CreateIncidentInput }) => incidentsApi.create(projectId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.incidents.list() }),
  };
}

export function useCreateIncidentMutation() {
  const queryClient = useQueryClient();
  return useMutation(createIncidentMutationOptions(queryClient));
}

export function runInvestigationMutationOptions(incidentId: number, queryClient: Pick<QueryClient, "invalidateQueries">) {
  return {
    mutationFn: (investigationId: number) => incidentsApi.runInvestigation(investigationId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.incidents.investigations(incidentId) }),
  };
}

export function useRunInvestigationMutation(incidentId: number) {
  const queryClient = useQueryClient();
  return useMutation(runInvestigationMutationOptions(incidentId, queryClient));
}

export function rootCauseMutationOptions(incidentId: number) {
  return { mutationFn: () => incidentsApi.generateRootCause(incidentId) };
}

export function useRootCauseMutation(incidentId: number) {
  return useMutation(rootCauseMutationOptions(incidentId));
}

export function usePatch(patchId: number | null) { return useQuery({ queryKey: patchId === null ? ["patches", "unresolved"] : queryKeys.patches.detail(patchId), queryFn: () => patchesApi.get(patchId!), enabled: patchId !== null }); }
export function useCreatePatchMutation() { const queryClient = useQueryClient(); return useMutation({ mutationFn: (input: CreatePatchInput) => patchesApi.create(input), onSuccess: (patch) => queryClient.invalidateQueries({ queryKey: queryKeys.patches.detail(patch.id) }) }); }
export function patchDecisionMutationOptions(patchId: number, queryClient: Pick<QueryClient, "invalidateQueries">) { return { mutationFn: ({ decision, note }: { decision: PatchDecision; note: string }) => patchesApi.decide(patchId, decision, note), onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.patches.detail(patchId) }) }; }
export function usePatchDecisionMutation(patchId: number) { const queryClient = useQueryClient(); return useMutation(patchDecisionMutationOptions(patchId, queryClient)); }
