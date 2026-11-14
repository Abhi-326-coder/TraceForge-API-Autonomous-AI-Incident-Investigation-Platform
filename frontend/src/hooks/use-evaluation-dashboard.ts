"use client";

import { useQuery } from "@tanstack/react-query";

import { evaluationsApi } from "@/lib/api/evaluations";
import { queryKeys } from "@/lib/query-keys";

export function useEvaluationDashboard() {
  return useQuery({ queryKey: queryKeys.evaluations.dashboard(), queryFn: evaluationsApi.getDashboard });
}
