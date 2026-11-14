export type ApiQueryValue = string | number | boolean | null | undefined;
export type ApiQuery = Record<string, ApiQueryValue | ApiQueryValue[]>;

export type ApiErrorPayload = {
  detail?: string;
  code?: string;
  [key: string]: unknown;
};

export class ApiError extends Error {
  public readonly status: number;
  public readonly payload: ApiErrorPayload | null;

  constructor(message: string, status: number, payload: ApiErrorPayload | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }

  get isUnauthorized() { return this.status === 401; }
}

export type ApiRequestOptions = Omit<RequestInit, "body" | "method"> & {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  query?: ApiQuery;
  body?: unknown;
};

function buildApiUrl(path: string, query?: ApiQuery) {
  const url = new URL(`/api/backend${path.startsWith("/") ? path : `/${path}`}`, "http://traceforge.local");
  for (const [key, value] of Object.entries(query ?? {})) {
    for (const item of Array.isArray(value) ? value : [value]) {
      if (item !== null && item !== undefined) url.searchParams.append(key, String(item));
    }
  }
  return `${url.pathname}${url.search}`;
}

async function readErrorPayload(response: Response): Promise<ApiErrorPayload | null> {
  if (!(response.headers.get("content-type") ?? "").includes("application/json")) return null;
  return response.json().catch(() => null) as Promise<ApiErrorPayload | null>;
}

function isJsonResponse(response: Response) {
  return (response.headers.get("content-type") ?? "").includes("json");
}

async function readSuccessPayload<T>(response: Response): Promise<T> {
  if (response.status === 204 || response.status === 205) return undefined as T;

  const text = await response.text();
  if (!text) return undefined as T;

  if (!isJsonResponse(response)) return text as T;

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError("Unable to parse the JSON response.", response.status);
  }
}

function notifySessionExpired() {
  if (typeof window !== "undefined") window.dispatchEvent(new Event("traceforge:session-expired"));
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, query, method = "GET", headers, ...requestOptions } = options;
  const requestHeaders = new Headers(headers);
  const serializedBody = body === undefined ? undefined : JSON.stringify(body);
  if (serializedBody) requestHeaders.set("Content-Type", "application/json");

  const response = await fetch(buildApiUrl(path, query), {
    ...requestOptions,
    method,
    headers: requestHeaders,
    body: serializedBody,
    credentials: "same-origin",
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = await readErrorPayload(response);
    const error = new ApiError(payload?.detail ?? `Request failed (${response.status}).`, response.status, payload);
    if (error.isUnauthorized) notifySessionExpired();
    throw error;
  }

  return readSuccessPayload<T>(response);
}

export const apiClient = {
  get: <T>(path: string, options?: Omit<ApiRequestOptions, "method" | "body">) => apiRequest<T>(path, options),
  post: <T>(path: string, body?: unknown, options?: Omit<ApiRequestOptions, "method" | "body">) => apiRequest<T>(path, { ...options, method: "POST", body }),
  put: <T>(path: string, body?: unknown, options?: Omit<ApiRequestOptions, "method" | "body">) => apiRequest<T>(path, { ...options, method: "PUT", body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<ApiRequestOptions, "method" | "body">) => apiRequest<T>(path, { ...options, method: "PATCH", body }),
  delete: <T>(path: string, options?: Omit<ApiRequestOptions, "method" | "body">) => apiRequest<T>(path, { ...options, method: "DELETE" }),
};
