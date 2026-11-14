import type { EvaluationDashboard } from "@/types/evaluation";
import { apiClient } from "@/lib/api-client";

export const evaluationsApi = {
  getDashboard: () => apiClient.get<EvaluationDashboard>("/api/evaluations/dashboard"),
};
