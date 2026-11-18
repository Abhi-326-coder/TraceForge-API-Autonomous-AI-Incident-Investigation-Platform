"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useGeneratePatchMutation } from "@/hooks/use-investigations";

export function GenerateAIPatch({ investigationId }: { investigationId?: number }) {
  const router = useRouter();
  const mutation = useGeneratePatchMutation();
  const generate = () => {
    if (!investigationId) return;
    mutation.mutate(investigationId, {
      onSuccess: (patch) => router.push(`/patches/${patch.id}?source=ai`),
    });
  };

  return (
    <section className="space-y-3 rounded-xl border border-accent/20 bg-accent/5 p-5">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-accent">AI generated proposal</p>
        <h2 className="mt-1 font-semibold text-foreground">Generate from investigation evidence</h2>
        <p className="mt-1 text-sm text-muted">TraceForge prepares a reviewable patch from referenced source files. Demo mode uses clearly labeled illustrative source content. Every patch remains pending human approval.</p>
      </div>
      {mutation.isError ? <p role="alert" className="text-sm text-danger">{mutation.error instanceof Error ? mutation.error.message : "Unable to generate an AI patch."}</p> : null}
      <Button type="button" onClick={generate} disabled={!investigationId || mutation.isPending}>
        {mutation.isPending ? "Generating patch…" : "Generate AI patch"}
      </Button>
      {!investigationId ? <p className="text-xs text-muted">Open this page from an investigation to generate an AI patch.</p> : null}
    </section>
  );
}
