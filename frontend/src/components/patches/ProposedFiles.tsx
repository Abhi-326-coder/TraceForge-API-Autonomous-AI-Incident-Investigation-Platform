"use client";

export function ProposedFiles({ files }: { files?: Record<string, string> | null }) {
  if (!files || Object.keys(files).length === 0) {
    return <p className="rounded-lg border border-dashed p-5 text-sm text-muted">Complete proposed file contents are unavailable from the current patch API. Review the unified diff; contents are not reconstructed from it.</p>;
  }
  return <div className="space-y-4">
    {Object.entries(files).map(([path, content]) => <section key={path} className="overflow-hidden rounded-lg border">
      <h3 className="border-b bg-surface-subtle px-4 py-2 font-mono text-xs font-medium">{path}</h3>
      <pre className="max-h-[32rem] overflow-auto bg-slate-950 p-4 text-xs leading-5 text-slate-100"><code>{content}</code></pre>
    </section>)}
  </div>;
}
