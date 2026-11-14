import assert from "node:assert/strict";
import test from "node:test";

import { validateProject } from "./project-validation.ts";

test("project validation requires a non-whitespace project name", () => {
  assert.deepEqual(validateProject({ name: "   " }), { name: "Enter a project name." });
});

test("project validation accepts a named project with an optional description", () => {
  assert.deepEqual(validateProject({ name: "Payments", description: "Payment processing" }), {});
});
