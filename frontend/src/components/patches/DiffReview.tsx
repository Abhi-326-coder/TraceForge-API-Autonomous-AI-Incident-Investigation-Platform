"use client";
import { classifyPatchDiffLine } from "@/lib/patch-review";

const lineStyles: Record<ReturnType<typeof classifyPatchDiffLine>, string> = {
  addition: "bg-emerald-950/70 text-emerald-200",
  deletion: "bg-rose-950/70 text-rose-200",
  header: "text-sky-200",
  context: "text-slate-200",
};

export function DiffReview({ diff }: { diff: string }) {
  if (!diff.trim()) return <p className="rounded-lg border border-dashed p-5 text-sm text-muted">No unified diff is available for this proposal.</p>;
  return (
    <div aria-label="Unified diff" className="max-h-[38rem] overflow-auto rounded-lg bg-slate-950 p-4 text-xs leading-5">
      <pre className="min-w-max font-mono"><code>{diff.split("\n").map((line, index) => {
        const kind = classifyPatchDiffLine(line);
        return <span key={`${index}-${line}`} className={`block whitespace-pre ${lineStyles[kind]}`}>{line || " "}</span>;
      })}</code></pre>
    </div>
  );
}
