import type { QueryClientConfig } from "@tanstack/react-query";

import { ApiError } from "./api-client.ts";

export const queryClientConfig: QueryClientConfig = {
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => !(error instanceof ApiError && error.status < 500) && failureCount < 1,
    },
    mutations: { retry: false },
  },
};
