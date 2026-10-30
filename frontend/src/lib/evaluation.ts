import type { EvaluationDashboard } from "@/types/evaluation";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getEvaluationDashboard(): Promise<EvaluationDashboard> {
  // Replace this with the same token retrieval mechanism
  // used by your existing authenticated API helper.
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  const response = await fetch(
    `${API_BASE_URL}/api/evaluations/dashboard`,
    {
      headers: token
        ? { Authorization: `Bearer ${token}` }
        : {},
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(`Unable to load evaluation dashboard (${response.status})`);
  }

  return response.json();
}