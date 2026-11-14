import assert from "node:assert/strict";
import test from "node:test";

import { createIncidentMutationOptions, patchDecisionMutationOptions, rootCauseMutationOptions, runInvestigationMutationOptions, startInvestigationMutationOptions } from "./use-investigations.ts";

test("starting an investigation invalidates only that incident's investigation cache", async () => {
  let invalidatedQueryKey: readonly unknown[] | undefined;
  const options = startInvestigationMutationOptions(27, {
    invalidateQueries: async (filters) => { invalidatedQueryKey = filters?.queryKey; },
  });

  await options.onSuccess();
  assert.deepEqual(invalidatedQueryKey, ["incidents", 27, "investigations"]);
});

test("creating an incident invalidates the incidents list", async () => {
  let invalidatedQueryKey: readonly unknown[] | undefined;
  await createIncidentMutationOptions({ invalidateQueries: async (filters) => { invalidatedQueryKey = filters?.queryKey; } }).onSuccess();
  assert.deepEqual(invalidatedQueryKey, ["incidents"]);
});

test("running an investigation refreshes that incident's investigation history", async () => {
  let invalidatedQueryKey: readonly unknown[] | undefined;
  await runInvestigationMutationOptions(27, { invalidateQueries: async (filters) => { invalidatedQueryKey = filters?.queryKey; } }).onSuccess();
  assert.deepEqual(invalidatedQueryKey, ["incidents", 27, "investigations"]);
});

test("root-cause mutation is explicit and has no durable cache to invalidate", () => {
  const options = rootCauseMutationOptions(27);
  assert.equal(typeof options.mutationFn, "function");
  assert.equal("onSuccess" in options, false);
});

test("patch decisions refresh only the decided patch", async () => {
  let invalidated: readonly unknown[] | undefined;
  const options = patchDecisionMutationOptions(19, { invalidateQueries: async (filters) => { invalidated = filters?.queryKey; } });
  await options.onSuccess();
  assert.deepEqual(invalidated, ["patches", 19]);
});
