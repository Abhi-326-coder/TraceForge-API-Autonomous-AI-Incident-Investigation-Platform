import assert from "node:assert/strict";
import test from "node:test";

import { validateIncident } from "./incident-validation.ts";

test("incident validation requires every backend create field and project query parameter", () => {
  assert.deepEqual(validateIncident({ projectId: null, title: "", description: "", service: "", severity: "" }), {
    projectId: "Select a project.", title: "Enter an incident title.", description: "Enter an incident description.", service: "Enter the affected service.", severity: "Select a severity.",
  });
});

test("incident validation accepts a complete create payload", () => {
  assert.deepEqual(validateIncident({ projectId: 3, title: "Checkout errors", description: "Requests fail", service: "checkout", severity: "HIGH" }), {});
});
