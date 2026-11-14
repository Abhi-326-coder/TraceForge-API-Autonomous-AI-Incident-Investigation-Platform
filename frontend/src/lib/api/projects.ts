import { apiClient } from "../api-client.ts";

export type Project = {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
};

export type CreateProjectInput = {
  name: string;
  description?: string;
};

export const projectsApi = {
  list: () => apiClient.get<Project[]>("/api/projects"),
  create: (input: CreateProjectInput) => apiClient.post<Project>("/api/projects", input),
};
