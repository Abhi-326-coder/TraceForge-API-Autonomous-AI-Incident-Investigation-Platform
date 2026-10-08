const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export async function getIncident(
  incidentId: number
) {
  const response = await fetch(
    `${API_URL}/api/incidents/${incidentId}`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch incident"
    );
  }

  return response.json();
}

export async function startInvestigation(
  incidentId: number
) {
  const response = await fetch(
    `${API_URL}/api/incidents/${incidentId}/investigate`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to start investigation"
    );
  }

  return response.json();
}
