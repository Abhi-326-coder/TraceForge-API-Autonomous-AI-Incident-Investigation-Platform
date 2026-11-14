import assert from "node:assert/strict";
import test from "node:test";

import { ApiError } from "./api-client.ts";
import { queryClientConfig } from "./query-client.ts";
import { queryKeys } from "./query-keys.ts";

test("query keys are stable and scoped by resource identity", () => {
  assert.deepEqual(queryKeys.projects.list(), ["projects"]);
  assert.deepEqual(queryKeys.projects.detail(7), ["projects", 7]);
  assert.deepEqual(queryKeys.incidents.detail(42), ["incidents", 42]);
  assert.deepEqual(queryKeys.incidents.investigations(42), ["incidents", 42, "investigations"]);
  assert.deepEqual(queryKeys.incidents.detailOrUnresolved(null), ["incidents", "unresolved"]);
  assert.deepEqual(queryKeys.incidents.investigationsOrUnresolved(null), ["incidents", "unresolved", "investigations"]);
});

test("query defaults do not retry client errors but retry one transient failure", () => {
  const retry = queryClientConfig.defaultOptions?.queries?.retry;
  assert.equal(typeof retry, "function");
  if (typeof retry !== "function") throw new Error("Expected query retry function.");

  assert.equal(retry(0, new ApiError("Not found", 404)), false);
  assert.equal(retry(0, new Error("Network failure")), true);
  assert.equal(retry(1, new Error("Network failure")), false);
});
