import { incidentsApi } from "./api/incidents";

export async function getIncident(
  incidentId: number
) {
  return incidentsApi.get(incidentId);
}

export async function startInvestigation(
  incidentId: number
) {
  return incidentsApi.startInvestigation(incidentId);
}
