import assert from "node:assert/strict";
import test from "node:test";

import { validateLogin } from "./auth-validation.ts";

test("validateLogin requires an email address", () => {
  assert.deepEqual(validateLogin("", "password"), { email: "Enter your email address." });
});

test("validateLogin rejects malformed email addresses", () => {
  assert.deepEqual(validateLogin("not-an-email", "password"), { email: "Enter a valid email address." });
});

test("validateLogin requires a password", () => {
  assert.deepEqual(validateLogin("engineer@traceforge.dev", ""), { password: "Enter your password." });
});

test("validateLogin accepts populated login credentials", () => {
  assert.deepEqual(validateLogin("engineer@traceforge.dev", "correct-horse-battery-staple"), {});
});
