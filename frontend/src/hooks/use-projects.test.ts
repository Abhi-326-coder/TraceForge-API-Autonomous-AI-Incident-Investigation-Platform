import assert from "node:assert/strict";
import test from "node:test";

import { createProjectMutationOptions } from "./use-projects.ts";

test("creating a project invalidates the projects list cache", async () => {
  let invalidatedQueryKey: readonly unknown[] | undefined;
  const options = createProjectMutationOptions({
    invalidateQueries: async (filters) => { invalidatedQueryKey = filters?.queryKey; },
  });

  await options.onSuccess();
  assert.deepEqual(invalidatedQueryKey, ["projects"]);
});
