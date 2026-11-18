"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import type { RootCause } from "@/types/investigation";
import { useRootCauseMutation } from "@/hooks/use-investigations";
import { Button } from "@/components/ui/Button";
import RootCauseCard from "./RootCauseCard";

export function RootCauseWorkspace({ incidentId, onEvidenceClick, initialResult = null }: { incidentId: number; onEvidenceClick: (evidenceId: number) => void; initialResult?: RootCause | null }) {
  const params = useParams<{ investigationId?: string }>();
  const [result, setResult] = useState<RootCause | null>(initialResult);
  const mutation = useRootCauseMutation(incidentId);
  return <section><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-medium uppercase tracking-wider text-muted">Root cause analysis</p><p className="mt-1 text-sm text-muted">Persisted analysis is available after refresh.</p></div><Button size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate(undefined, { onSuccess: setResult })}>{mutation.isPending ? "Generating…" : result ? "Generate again" : "Generate analysis"}</Button></div>{mutation.isError ? <p role="alert" className="mt-3 text-sm text-danger">{mutation.error instanceof Error ? mutation.error.message : "Unable to generate root-cause analysis."}</p> : null}<div className="mt-4"><RootCauseCard rootCause={result} onEvidenceClick={onEvidenceClick} /></div>{params.investigationId ? <div className="mt-4 border-t pt-4"><p className="text-sm text-muted">Generate an AI patch from investigation evidence and source context.</p><Link className="mt-2 inline-flex text-sm font-medium text-accent hover:underline" href={`/patches/new?investigationId=${params.investigationId}`}>Open patch generator</Link></div> : null}</section>;
}
