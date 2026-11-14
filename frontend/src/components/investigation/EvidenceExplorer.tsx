"use client";

import { useMemo, useState } from "react";
import { Copy } from "lucide-react";

import type { Evidence } from "@/types/investigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { EmptyState } from "@/components/ui/States";

export function EvidenceExplorer({ evidence, selectedEvidenceId, onSelect }: { evidence: Evidence[]; selectedEvidenceId?: number | null; onSelect?: (id: number) => void }) {
  const [search, setSearch] = useState("");
  const [copied, setCopied] = useState<number | null>(null);
  const visible = useMemo(() => {
    const term = search.trim().toLowerCase();
    return !term ? evidence : evidence.filter((item) => [item.id, item.provider, item.source_type, item.title, item.content, item.source_reference].filter(Boolean).join(" ").toLowerCase().includes(term));
  }, [evidence, search]);
  const selected = evidence.find((item) => item.id === selectedEvidenceId) ?? null;
  const copyReference = async (item: Evidence) => {
    if (!item.source_reference || !navigator.clipboard) return;
    await navigator.clipboard.writeText(item.source_reference);
    setCopied(item.id);
  };
  if (!evidence.length) return <EmptyState title="No evidence collected" description="Evidence will appear here when the investigation records it." />;
  return <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(260px,0.7fr)]"><div><Input aria-label="Search evidence" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search evidence" />{!visible.length ? <p className="mt-4 text-sm text-muted">No evidence matches this search.</p> : <div className="mt-4 space-y-2">{visible.map((item) => <button type="button" key={item.id} onClick={() => onSelect?.(item.id)} className="w-full rounded-lg border bg-surface p-4 text-left hover:bg-surface-subtle"><div className="flex items-center justify-between gap-3"><span className="text-xs font-medium text-muted">{item.provider} · {item.source_type}</span><span className="font-mono text-xs text-muted">#{item.id}</span></div><p className="mt-2 text-sm font-medium text-foreground">{item.title}</p><p className="mt-1 line-clamp-2 text-xs text-muted">{item.content}</p></button>)}</div>}</div><aside className="rounded-lg border bg-surface p-4">{selected ? <><p className="text-xs font-medium uppercase tracking-wide text-muted">Evidence #{selected.id}</p><h3 className="mt-2 text-sm font-semibold text-foreground">{selected.title}</h3><dl className="mt-4 space-y-2 text-xs"><div><dt className="text-muted">Source</dt><dd>{selected.provider} · {selected.source_type}</dd></div><div><dt className="text-muted">Timestamp</dt><dd>{new Date(selected.created_at).toLocaleString()}</dd></div>{selected.source_reference ? <div><dt className="text-muted">Reference</dt><dd className="mt-1 flex items-start gap-2 break-all"><span>{selected.source_reference}</span><Button size="sm" variant="ghost" aria-label="Copy reference" onClick={() => void copyReference(selected)}><Copy size={14} />{copied === selected.id ? "Copied" : "Copy"}</Button></dd></div> : null}</dl><p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-foreground">{selected.content}</p></> : <p className="text-sm text-muted">Select an evidence item to inspect its details.</p>}</aside></div>;
}
