import { evaluationsApi } from "./api/evaluations";
import type { EvaluationDashboard } from "@/types/evaluation";

export async function getEvaluationDashboard(): Promise<EvaluationDashboard> {
  return evaluationsApi.getDashboard();
}
