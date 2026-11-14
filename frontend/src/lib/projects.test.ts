import assert from "node:assert/strict";
import test from "node:test";

import { projectsApi } from "./api/projects.ts";

const originalFetch = globalThis.fetch;

test("projects API lists projects through the authenticated BFF", async () => {
  let capturedUrl = "";
  globalThis.fetch = async (input) => {
    capturedUrl = String(input);
    return new Response(JSON.stringify([{ id: 4, name: "Payments", description: null, created_at: "2026-01-01T00:00:00Z" }]), {
      headers: { "Content-Type": "application/json" },
    });
  };

  const projects = await projectsApi.list();
  assert.equal(capturedUrl, "/api/backend/api/projects");
  assert.equal(projects[0]?.name, "Payments");
  globalThis.fetch = originalFetch;
});

test("projects API creates a project through the BFF", async () => {
  let capturedInit: RequestInit | undefined;
  globalThis.fetch = async (_input, init) => {
    capturedInit = init;
    return new Response(JSON.stringify({ id: 5, name: "Checkout", description: "Payments service", created_at: "2026-01-01T00:00:00Z" }), {
      headers: { "Content-Type": "application/json" },
    });
  };

  const project = await projectsApi.create({ name: "Checkout", description: "Payments service" });
  assert.equal(project.id, 5);
  assert.equal(capturedInit?.method, "POST");
  assert.equal(capturedInit?.body, JSON.stringify({ name: "Checkout", description: "Payments service" }));
  globalThis.fetch = originalFetch;
});
