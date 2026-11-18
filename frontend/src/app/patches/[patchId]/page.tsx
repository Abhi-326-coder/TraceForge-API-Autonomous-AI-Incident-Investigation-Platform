"use client";

import Link from "next/link";
import { use } from "react";
import { DiffReview } from "@/components/patches/DiffReview";
import { PatchDecisionPanel } from "@/components/patches/PatchDecisionPanel";
import { ProposedFiles } from "@/components/patches/ProposedFiles";
import { StatusBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingSkeleton } from "@/components/ui/States";
import { usePatch } from "@/hooks/use-investigations";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { patchesApi } from "@/lib/api/patches";

type Props = { params: Promise<{ patchId: string }>; searchParams: Promise<{ source?: string }> };

export default function PatchPage({ params, searchParams }: Props) {
  const { patchId: raw } = use(params);
  const { source } = use(searchParams);
  const patchId = Number(raw);
  const query = usePatch(Number.isInteger(patchId) && patchId > 0 ? patchId : null);
  const queryClient = useQueryClient();
  const [githubMessage, setGithubMessage] = useState<string | null>(null);
  const branchMutation = useMutation({ mutationFn: () => patchesApi.createBranch(patchId), onSuccess: async (result) => { setGithubMessage(result.simulated ? result.message ?? "Demo only: branch creation was simulated; no GitHub branch was written." : `Branch ${result.branch_name} created.`); await queryClient.invalidateQueries({ queryKey: ["patches", patchId] }); }, onError: (error) => setGithubMessage(error instanceof Error ? error.message : "Unable to create branch. Check the project GitHub connection.") });
  const prMutation = useMutation({ mutationFn: () => patchesApi.createPullRequest(patchId), onSuccess: async (result) => { setGithubMessage(result.simulated ? result.message ?? "Demo only: no real pull request was created." : result.pr_url ? `Draft pull request created: ${result.pr_url}` : "Pull request request completed."); await queryClient.invalidateQueries({ queryKey: ["patches", patchId] }); }, onError: (error) => setGithubMessage(error instanceof Error ? error.message : "Unable to create pull request. Check the project GitHub connection and credentials.") });

  if (!Number.isInteger(patchId) || patchId <= 0) return <ErrorState title="Invalid patch" description="The patch ID must be a positive number." />;
  if (query.isLoading) return <LoadingSkeleton className="h-64 w-full" />;
  if (query.isError) return <ErrorState title={query.error && typeof query.error === "object" && "status" in query.error && (query.error as { status: number }).status === 404 ? "Patch not found" : "Unable to load patch"} description={query.error instanceof Error ? query.error.message : "Unable to load patch."} onRetry={() => void query.refetch()} />;
  const patch = query.data;
  if (!patch) return <ErrorState title="Patch not found" description="This patch is unavailable." />;

  return <main className="space-y-6">
    <header className="flex flex-wrap items-start justify-between gap-4">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-xs font-medium uppercase tracking-wider text-muted">{source === "ai" ? "AI generated proposal · Human review required" : "Remediation proposal"}</p>
          {source === "ai" ? <span className="rounded-full bg-accent/10 px-2.5 py-1 text-xs font-medium text-accent">AI generated</span> : null}
        </div>
        <h1 className="mt-2 break-words text-2xl font-semibold">{patch.patch_summary}</h1>
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted">
          <span>Patch #{patch.id}</span>
          <span>Investigation <Link className="text-accent hover:underline" href={`/investigations/${patch.investigation_id}`}>#{patch.investigation_id}</Link></span>
          <time dateTime={patch.created_at}>Created {new Date(patch.created_at).toLocaleString()}</time>
        </div>
      </div>
      <StatusBadge status={patch.status} />
    </header>

    <Card className="p-5">
      <h2 className="font-semibold">Change summary</h2>
      <p className="mt-1 text-sm text-muted">{patch.changed_files.length} changed {patch.changed_files.length === 1 ? "file" : "files"}</p>
      <div className="mt-4 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <List title="Changed files" values={patch.changed_files} empty="No changed files listed." mono />
        <List title="Tests to run" values={patch.tests_to_run} empty="No tests specified." />
        <List title="Risks" values={patch.risks} empty="No risks listed." />
        <List title="Assumptions" values={patch.assumptions ?? []} empty="Assumptions are unavailable from the current patch API." />
      </div>
    </Card>

    <div className="grid gap-6 xl:grid-cols-3">
      <div className="space-y-6 xl:col-span-2">
        <Card className="p-5 sm:p-6"><div className="flex items-center justify-between gap-3"><h2 className="font-semibold">Unified diff</h2><span className="text-xs text-muted">Additions and deletions highlighted</span></div><div className="mt-4"><DiffReview diff={patch.diff} /></div></Card>
        <Card className="space-y-4 p-5 sm:p-6"><div><h2 className="font-semibold">Proposed file contents</h2><p className="mt-1 text-sm text-muted">Complete generated files, when provided by the patch API.</p></div><ProposedFiles files={patch.proposed_files} /></Card>
      </div>
      <aside className="space-y-5">
        <PatchDecisionPanel patch={patch} onConflict={() => void query.refetch()} />
        {patch.status === "APPROVED" ? <Card className="space-y-3 p-5"><h2 className="font-semibold">GitHub workflow</h2>{patch.github_pr_state === "SIMULATED" ? <p className="text-sm text-amber-700">Demo result: GitHub operations were simulated. No branch, commit, or pull request exists.</p> : patch.github_pr_url ? <p className="text-sm text-success">Draft PR <a className="underline" href={patch.github_pr_url} target="_blank" rel="noreferrer">#{patch.github_pr_number}</a> is {patch.github_pr_state}.</p> : patch.github_branch ? <p className="text-sm text-muted">Branch ready: {patch.github_branch}{patch.github_branch_sha === "SIMULATED" ? " (simulated; no GitHub resource created)" : ""}</p> : <p className="text-sm text-muted">Patch approval is required before GitHub operations are available.</p>}{githubMessage ? <p role="status" className="text-sm text-muted">{githubMessage}</p> : null}<div className="flex flex-wrap gap-2"><Button size="sm" variant="secondary" disabled={branchMutation.isPending || Boolean(patch.github_branch)} onClick={() => branchMutation.mutate()}>{branchMutation.isPending ? "Creating branch…" : patch.github_branch ? "Branch created" : "Create branch"}</Button><Button size="sm" disabled={prMutation.isPending || !patch.github_branch || Boolean(patch.github_pr_state)} onClick={() => prMutation.mutate()}>{prMutation.isPending ? "Creating PR…" : patch.github_pr_state === "SIMULATED" ? "PR simulated" : patch.github_pr_url ? "PR created" : "Create draft PR"}</Button></div><p className="text-xs text-muted">Real GitHub writes use the project’s configured repository. Demo mode records simulated results only.</p></Card> : null}
        {patch.status !== "PENDING" ? <Card className="p-5"><h2 className="font-semibold">Decision recorded</h2><p className="mt-2 text-sm text-muted">This patch is {patch.status.toLowerCase()}; no further decision actions are available.</p>{patch.decision_note ? <div className="mt-4 border-t pt-4"><p className="text-xs font-medium uppercase text-muted">Decision note</p><p className="mt-1 whitespace-pre-wrap text-sm">{patch.decision_note}</p></div> : null}{patch.decided_by ? <p className="mt-3 text-xs text-muted">Decided by {patch.decided_by}{patch.decided_at ? ` · ${new Date(patch.decided_at).toLocaleString()}` : ""}</p> : null}</Card> : null}
      </aside>
    </div>
  </main>;
}

function List({ title, values, empty, mono = false }: { title: string; values: string[]; empty: string; mono?: boolean }) {
  return <section className="min-w-0"><h3 className="text-xs font-semibold uppercase tracking-wide text-muted">{title}</h3>{values.length ? <ul className="mt-2 space-y-1.5">{values.map((value, index) => <li key={`${index}-${value}`} className={`break-words text-sm ${mono ? "font-mono" : ""}`}>{value}</li>)}</ul> : <p className="mt-2 text-sm text-muted">{empty}</p>}</section>;
}
