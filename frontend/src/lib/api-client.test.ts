import assert from "node:assert/strict";
import test from "node:test";

import { ApiError, apiClient } from "./api-client.ts";

const originalFetch = globalThis.fetch;

test("apiClient sends same-origin BFF requests with query parameters and JSON bodies", async () => {
  let capturedUrl = "";
  let capturedInit: RequestInit | undefined;
  globalThis.fetch = async (input, init) => {
    capturedUrl = String(input);
    capturedInit = init;
    return new Response(JSON.stringify({ id: 7 }), { headers: { "Content-Type": "application/json" } });
  };

  const result = await apiClient.post<{ id: number }>("/api/incidents", { title: "Timeout" }, { query: { project_id: 12, labels: ["api", "urgent"] } });

  assert.deepEqual(result, { id: 7 });
  assert.equal(capturedUrl, "/api/backend/api/incidents?project_id=12&labels=api&labels=urgent");
  assert.equal(capturedInit?.method, "POST");
  assert.equal(capturedInit?.credentials, "same-origin");
  assert.equal(capturedInit?.cache, "no-store");
  assert.equal(capturedInit?.body, JSON.stringify({ title: "Timeout" }));
  assert.equal(new Headers(capturedInit?.headers).get("content-type"), "application/json");
  globalThis.fetch = originalFetch;
});

test("apiClient exposes structured backend errors", async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: "Incident not found.", code: "NOT_FOUND" }), {
    status: 404,
    headers: { "Content-Type": "application/json" },
  });

  await assert.rejects(
    () => apiClient.get("/api/incidents/404"),
    (error: unknown) => error instanceof ApiError && error.status === 404 && error.message === "Incident not found." && error.payload?.code === "NOT_FOUND",
  );
  globalThis.fetch = originalFetch;
});

test("apiClient returns undefined for successful empty responses", async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });
  assert.equal(await apiClient.delete<void>("/api/resource/1"), undefined);
  globalThis.fetch = originalFetch;
});

test("apiClient returns text for successful non-JSON responses", async () => {
  globalThis.fetch = async () => new Response("investigation started", { headers: { "Content-Type": "text/plain" } });
  assert.equal(await apiClient.get<string>("/api/status"), "investigation started");
  globalThis.fetch = originalFetch;
});

test("apiClient returns undefined for an empty successful response", async () => {
  globalThis.fetch = async () => new Response(null, { status: 200 });
  assert.equal(await apiClient.get<void>("/api/status"), undefined);
  globalThis.fetch = originalFetch;
});

test("apiClient reports malformed successful JSON responses", async () => {
  globalThis.fetch = async () => new Response("{not json", { headers: { "Content-Type": "application/json" } });
  await assert.rejects(
    () => apiClient.get("/api/status"),
    (error: unknown) => error instanceof ApiError && error.status === 200 && error.message === "Unable to parse the JSON response.",
  );
  globalThis.fetch = originalFetch;
});

test("apiClient dispatches a session-expiry event for unauthorized responses", async () => {
  const windowDescriptor = Object.getOwnPropertyDescriptor(globalThis, "window");
  const eventTarget = new EventTarget();
  let eventCount = 0;
  eventTarget.addEventListener("traceforge:session-expired", () => { eventCount += 1; });
  Object.defineProperty(globalThis, "window", { configurable: true, value: eventTarget });
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: "Authentication required." }), {
    status: 401,
    headers: { "Content-Type": "application/json" },
  });

  await assert.rejects(() => apiClient.get("/api/status"), ApiError);
  assert.equal(eventCount, 1);
  globalThis.fetch = originalFetch;
  if (windowDescriptor) Object.defineProperty(globalThis, "window", windowDescriptor);
  else delete (globalThis as { window?: unknown }).window;
});
