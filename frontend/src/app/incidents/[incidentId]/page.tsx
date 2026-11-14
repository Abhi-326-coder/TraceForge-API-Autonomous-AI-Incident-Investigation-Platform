"use client";

import { use, useEffect, useState } from "react";

import { Badge, StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState, LoadingSkeleton } from "@/components/ui/States";
import EvidencePanel from "@/components/investigation/EvidencePanel";
import IncidentHeader from "@/components/investigation/IncidentHeader";
import InvestigationTimeline from "@/components/investigation/InvestigationTimeline";
import RootCauseCard from "@/components/investigation/RootCauseCard";
import { useIncident, useIncidentInvestigations, useIncidentLogs, useIncidentMetrics, useRunInvestigationMutation, useStartInvestigationMutation } from "@/hooks/use-investigations";
import { useProjects } from "@/hooks/use-projects";
import { connectInvestigationEvents } from "@/lib/sse";
import type { Evidence, InvestigationEvent, RootCause } from "@/types/investigation";

type Props = { params: Promise<{ incidentId: string }> };

export default function IncidentPage({ params }: Props) {
  const { incidentId: incidentIdParam } = use(params);
  const incidentId = Number(incidentIdParam);
  const validIncidentId = Number.isInteger(incidentId);
  const [events, setEvents] = useState<InvestigationEvent[]>([]);
  const [evidence] = useState<Evidence[]>([]);
  const [rootCause, setRootCause] = useState<RootCause | null>(null);
  const [streamStatus, setStreamStatus] = useState<"connecting" | "connected" | "error" | "idle">("idle");
  const [streamError, setStreamError] = useState<string | null>(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [queuedInvestigationIds, setQueuedInvestigationIds] = useState<Set<number>>(() => new Set());
  const incidentQuery = useIncident(validIncidentId ? incidentId : null);
  const investigationsQuery = useIncidentInvestigations(validIncidentId ? incidentId : null);
  const logsQuery = useIncidentLogs(validIncidentId ? incidentId : null);
  const metricsQuery = useIncidentMetrics(validIncidentId ? incidentId : null);
  const projectsQuery = useProjects();
  const createInvestigation = useStartInvestigationMutation(incidentId);
  const runInvestigation = useRunInvestigationMutation(incidentId);
  const incident = incidentQuery.data;
  const investigationId = investigationsQuery.data?.at(-1)?.id ?? null;
  const project = projectsQuery.data?.find((item) => item.id === incident?.project_id);
  const displayedStreamStatus = investigationId ? streamStatus : "idle";

  useEffect(() => {
    if (!investigationId) return;
    return connectInvestigationEvents(investigationId, (event) => {
      setEvents((current) => [...current, event]);
      if (event.event_type === "root_cause_completed") setRootCause(event.data as unknown as RootCause);
    }, { onStatus: (status) => { setStreamStatus(status); if (status === "connected") setStreamError(null); }, onError: setStreamError });
  }, [investigationId, reconnectAttempt]);

  if (incidentQuery.isError) return <ErrorState description={incidentQuery.error instanceof Error ? incidentQuery.error.message : "Unable to load this incident."} onRetry={() => { void incidentQuery.refetch(); }} />;
  if (!incident) return <LoadingSkeleton className="h-64 w-full" />;

  return (
    <main className="space-y-6">
      <IncidentHeader incident={incident} />
      <div className="flex flex-wrap items-center gap-3"><Button disabled={!validIncidentId || createInvestigation.isPending} onClick={() => createInvestigation.mutate()}>{createInvestigation.isPending ? "Creating investigation…" : "Create investigation"}</Button>{createInvestigation.isError ? <p className="text-sm text-danger" role="alert">{createInvestigation.error instanceof Error ? createInvestigation.error.message : "Unable to create the investigation."}</p> : null}</div>
      <div className="grid gap-4 md:grid-cols-3"><Card className="p-4"><p className="text-xs font-medium uppercase tracking-wide text-muted">Project</p><p className="mt-2 text-sm font-medium text-foreground">{projectsQuery.isLoading ? "Loading project…" : project?.name ?? `Project #${incident.project_id}`}</p></Card><Card className="p-4"><p className="text-xs font-medium uppercase tracking-wide text-muted">Created</p><p className="mt-2 text-sm font-medium text-foreground">{new Date(incident.created_at).toLocaleString()}</p></Card><Card className="p-4"><p className="text-xs font-medium uppercase tracking-wide text-muted">Incident status</p><div className="mt-2"><StatusBadge status={incident.status} /></div></Card></div>
      <div className="grid gap-6 xl:grid-cols-12"><section className="rounded-xl border bg-surface p-6 xl:col-span-7"><p className="text-xs font-medium uppercase tracking-wider text-muted">Investigation</p><h2 className="mt-1 text-lg font-semibold">Live investigation timeline</h2><div className="mt-2 flex flex-wrap items-center gap-3 text-sm"><span className={displayedStreamStatus === "connected" ? "text-success" : displayedStreamStatus === "error" ? "text-danger" : "text-muted"}>{displayedStreamStatus === "connected" ? "Live updates connected" : displayedStreamStatus === "connecting" ? "Connecting to live updates…" : displayedStreamStatus === "error" ? "Live updates disconnected" : "No live investigation selected"}</span>{displayedStreamStatus === "error" ? <Button size="sm" variant="secondary" onClick={() => { setStreamError(null); setReconnectAttempt((attempt) => attempt + 1); }}>Reconnect</Button> : null}</div>{streamError ? <p className="mt-2 text-sm text-danger" role="alert">{streamError}</p> : null}<div className="mt-6"><InvestigationTimeline events={events} /></div></section><aside className="space-y-6 xl:col-span-5"><section><p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted">Root cause</p><RootCauseCard rootCause={rootCause} /></section><section><p className="mb-3 text-xs font-medium uppercase tracking-wider text-muted">Evidence</p><EvidencePanel evidence={evidence} /></section></aside></div>
      <Card className="p-6"><p className="text-xs font-medium uppercase tracking-wider text-muted">Investigations</p><h2 className="mt-1 text-lg font-semibold">Investigation history</h2>{investigationsQuery.isLoading ? <LoadingSkeleton className="mt-4 h-24 w-full" /> : null}{investigationsQuery.isError ? <div className="mt-4"><ErrorState title="Unable to load investigations" description={investigationsQuery.error instanceof Error ? investigationsQuery.error.message : "Unable to load investigation history."} onRetry={() => { void investigationsQuery.refetch(); }} /></div> : null}{!investigationsQuery.isLoading && !investigationsQuery.isError && investigationsQuery.data?.length === 0 ? <p className="mt-4 text-sm text-muted">No investigations have been created for this incident.</p> : null}{investigationsQuery.data?.length ? <div className="mt-4 overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><thead className="text-xs uppercase tracking-wide text-muted"><tr><th className="pb-3">ID</th><th className="pb-3">Status</th><th className="pb-3">Stage</th><th className="pb-3">Created</th><th className="pb-3" /></tr></thead><tbody>{investigationsQuery.data.map((investigation) => <tr key={investigation.id} className="border-t"><td className="py-3 font-medium">#{investigation.id}</td><td className="py-3"><StatusBadge status={investigation.status} /></td><td className="py-3 text-muted">{investigation.current_stage}</td><td className="py-3 text-muted">{new Date(investigation.created_at).toLocaleString()}</td><td className="py-3 text-right">{investigation.status === "QUEUED" ? <Button size="sm" disabled={runInvestigation.isPending || queuedInvestigationIds.has(investigation.id)} onClick={() => runInvestigation.mutate(investigation.id, { onSuccess: () => setQueuedInvestigationIds((current) => new Set(current).add(investigation.id)) })}>{queuedInvestigationIds.has(investigation.id) ? "Queued" : runInvestigation.isPending ? "Queueing…" : "Run"}</Button> : null}</td></tr>)}</tbody></table></div> : null}{runInvestigation.isError ? <p className="mt-4 text-sm text-danger" role="alert">{runInvestigation.error instanceof Error ? runInvestigation.error.message : "Unable to queue this investigation."}</p> : null}</Card>
      <div className="grid gap-6 xl:grid-cols-2"><Card className="p-6"><p className="text-xs font-medium uppercase tracking-wider text-muted">Observability</p><h2 className="mt-1 text-lg font-semibold">Metrics</h2>{metricsQuery.isLoading ? <LoadingSkeleton className="mt-4 h-28 w-full" /> : null}{metricsQuery.isError ? <div className="mt-4"><ErrorState title="Unable to load metrics" description={metricsQuery.error instanceof Error ? metricsQuery.error.message : "Unable to load metrics."} onRetry={() => { void metricsQuery.refetch(); }} /></div> : null}{metricsQuery.data ? <div className="mt-4 grid grid-cols-2 gap-3 text-sm"><Metric label="Request rate" value={String(metricsQuery.data.request_rate)} /><Metric label="Error rate" value={`${metricsQuery.data.error_rate}%`} /><Metric label="Latency" value={`${metricsQuery.data.latency_ms} ms`} /><Metric label="DB connections" value={`${metricsQuery.data.database_connections} / ${metricsQuery.data.database_connection_limit}`} /></div> : null}</Card><Card className="p-6"><p className="text-xs font-medium uppercase tracking-wider text-muted">Observability</p><h2 className="mt-1 text-lg font-semibold">Logs</h2>{logsQuery.isLoading ? <LoadingSkeleton className="mt-4 h-28 w-full" /> : null}{logsQuery.isError ? <div className="mt-4"><ErrorState title="Unable to load logs" description={logsQuery.error instanceof Error ? logsQuery.error.message : "Unable to load logs."} onRetry={() => { void logsQuery.refetch(); }} /></div> : null}{logsQuery.data?.length === 0 ? <p className="mt-4 text-sm text-muted">No logs available.</p> : null}{logsQuery.data?.length ? <div className="mt-4 max-h-72 space-y-3 overflow-y-auto">{logsQuery.data.map((log, index) => <div key={`${log.timestamp}-${index}`} className="rounded-lg bg-surface-subtle p-3 text-xs"><div className="flex flex-wrap gap-2"><Badge tone={log.level.toLowerCase().includes("error") ? "danger" : "neutral"}>{log.level}</Badge><span className="text-muted">{log.timestamp}</span><span className="text-muted">{log.service}</span></div><p className="mt-2 font-mono text-foreground">{log.message}</p></div>)}</div> : null}</Card></div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg bg-surface-subtle p-3"><p className="text-xs text-muted">{label}</p><p className="mt-1 font-medium text-foreground">{value}</p></div>;
}
