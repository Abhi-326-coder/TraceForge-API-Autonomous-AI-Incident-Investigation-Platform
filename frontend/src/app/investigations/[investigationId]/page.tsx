"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { useQueries } from "@tanstack/react-query";
import { EvidenceExplorer } from "@/components/investigation/EvidenceExplorer";
import InvestigationTimeline from "@/components/investigation/InvestigationTimeline";
import { RootCauseWorkspace } from "@/components/investigation/RootCauseWorkspace";
import { StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState, LoadingSkeleton } from "@/components/ui/States";
import { useIncidents, useInvestigationEvidence } from "@/hooks/use-investigations";
import { incidentsApi } from "@/lib/api/incidents";
import { queryKeys } from "@/lib/query-keys";
import { appendUniqueInvestigationEvent, connectInvestigationEvents, type InvestigationStreamStatus } from "@/lib/sse";
import type { InvestigationEvent } from "@/types/investigation";

type Props = { params: Promise<{ investigationId: string }> };

export default function InvestigationWorkspacePage({ params }: Props) {
  const { investigationId: rawId } = use(params);
  const investigationId = Number(rawId);
  const validId = Number.isInteger(investigationId) && investigationId > 0;
  const incidentsQuery = useIncidents();
  const investigationQueries = useQueries({ queries: (incidentsQuery.data ?? []).map((incident) => ({ queryKey: queryKeys.incidents.investigations(incident.id), queryFn: () => incidentsApi.listInvestigations(incident.id) })) });
  const found = investigationQueries.flatMap((query) => query.data ?? []).find((investigation) => investigation.id === investigationId);
  const evidenceQuery = useInvestigationEvidence(validId ? investigationId : null);
  const [events, setEvents] = useState<InvestigationEvent[]>([]);
  const [streamStatus, setStreamStatus] = useState<InvestigationStreamStatus>("connecting");
  const [streamError, setStreamError] = useState<string | null>(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<number | null>(null);
  useEffect(() => {
    if (!validId) return;
    return connectInvestigationEvents(investigationId, (event) => setEvents((current) => appendUniqueInvestigationEvent(current, event)), { onStatus: (status) => { setStreamStatus(status); if (status === "connected") setStreamError(null); }, onError: setStreamError });
  }, [investigationId, validId, reconnectAttempt]);
  if (!validId) return <ErrorState title="Invalid investigation" description="The investigation ID must be a positive number." />;
  if (incidentsQuery.isError) return <ErrorState title="Unable to load investigation" description={incidentsQuery.error instanceof Error ? incidentsQuery.error.message : "Unable to load incidents."} onRetry={() => void incidentsQuery.refetch()} />;
  if (incidentsQuery.isLoading || investigationQueries.some((query) => query.isLoading)) return <LoadingSkeleton className="h-64 w-full" />;
  if (investigationQueries.some((query) => query.isError)) return <ErrorState title="Unable to load investigation" description="Investigation history could not be loaded." onRetry={() => investigationQueries.forEach((query) => void query.refetch())} />;
  if (!found) return <ErrorState title="Investigation not found" description="This investigation is unavailable or you do not have access to its incident." />;
  return <main className="space-y-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-medium uppercase tracking-wider text-muted">Investigation workspace</p><h1 className="mt-1 text-2xl font-semibold text-foreground">Investigation #{found.id}</h1><p className="mt-2 text-sm text-muted">Incident <Link className="font-medium text-accent hover:underline" href={`/incidents/${found.incident_id}`}>#{found.incident_id}</Link></p></div><StatusBadge status={found.status} /></div><div className="grid gap-4 md:grid-cols-4"><Meta label="Current stage" value={found.current_stage} /><Meta label="Created" value={formatDate(found.created_at)} /><Meta label="Started" value={formatDate(found.started_at)} /><Meta label="Completed" value={formatDate(found.completed_at)} /></div><Card className="p-6"><RootCauseWorkspace incidentId={found.incident_id} onEvidenceClick={setSelectedEvidenceId} /></Card><div className="grid gap-6 xl:grid-cols-12"><Card className="p-6 xl:col-span-7"><p className="text-xs font-medium uppercase tracking-wider text-muted">Live timeline</p><div className="mt-2 flex flex-wrap items-center gap-3"><span className={streamStatus === "connected" ? "text-sm text-success" : streamStatus === "error" ? "text-sm text-danger" : "text-sm text-muted"}>{streamStatus === "connected" ? "Live updates connected" : streamStatus === "error" ? "Live updates disconnected" : "Connecting to live updates…"}</span>{streamStatus === "error" ? <Button size="sm" variant="secondary" onClick={() => { setStreamError(null); setReconnectAttempt((value) => value + 1); }}>Reconnect</Button> : null}</div>{streamError ? <p role="alert" className="mt-2 text-sm text-danger">{streamError}</p> : null}<div className="mt-6">{events.length ? <InvestigationTimeline events={events} onEvidenceClick={setSelectedEvidenceId} /> : <p className="text-sm text-muted">No timeline events have been received yet.</p>}</div></Card><Card className="p-6 xl:col-span-5"><p className="text-xs font-medium uppercase tracking-wider text-muted">Evidence</p><h2 className="mt-1 text-lg font-semibold">Collected evidence</h2><div className="mt-4">{evidenceQuery.isLoading ? <LoadingSkeleton className="h-40 w-full" /> : evidenceQuery.isError ? <ErrorState title="Unable to load evidence" description={evidenceQuery.error instanceof Error ? evidenceQuery.error.message : "Unable to load evidence."} onRetry={() => void evidenceQuery.refetch()} /> : <EvidenceExplorer evidence={evidenceQuery.data ?? []} selectedEvidenceId={selectedEvidenceId} onSelect={setSelectedEvidenceId} />}</div></Card></div></main>;
}
function Meta({ label, value }: { label: string; value: string }) { return <Card className="p-4"><p className="text-xs font-medium uppercase tracking-wide text-muted">{label}</p><p className="mt-2 text-sm font-medium text-foreground">{value}</p></Card>; }
function formatDate(value: string | null) { return value ? new Date(value).toLocaleString() : "Not available"; }
