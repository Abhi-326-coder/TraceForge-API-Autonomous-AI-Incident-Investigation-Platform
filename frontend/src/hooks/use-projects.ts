"use client";

import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import { projectsApi, type CreateProjectInput } from "../lib/api/projects.ts";
import { queryKeys } from "../lib/query-keys.ts";

export function useProjects() {
  return useQuery({
    queryKey: queryKeys.projects.list(),
    queryFn: projectsApi.list,
  });
}

export function createProjectMutationOptions(queryClient: Pick<QueryClient, "invalidateQueries">) {
  return {
    mutationFn: (input: CreateProjectInput) => projectsApi.create(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.projects.list() }),
  };
}

export function useCreateProjectMutation() {
  const queryClient = useQueryClient();
  return useMutation(createProjectMutationOptions(queryClient));
}
