"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { CreateIncidentDialog } from "@/components/incidents/CreateIncidentDialog";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingSkeleton } from "@/components/ui/States";
import { useIncidents } from "@/hooks/use-investigations";
import { useProjects } from "@/hooks/use-projects";
import { PageHeader } from "@/components/ui/PageHeader";

export default function IncidentsPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");
  const [projectId, setProjectId] = useState("all");
  const incidentsQuery = useIncidents();
  const projectsQuery = useProjects();
  const projectById = useMemo(() => new Map(projectsQuery.data?.map((project) => [project.id, project.name])), [projectsQuery.data]);
  const visibleIncidents = useMemo(() => {
    const query = search.trim().toLowerCase();
    return (incidentsQuery.data ?? [])
      .filter((incident) => projectById.has(incident.project_id))
      .filter((incident) => !query || incident.title.toLowerCase().includes(query) || incident.description.toLowerCase().includes(query))
      .filter((incident) => severity === "all" || incident.severity === severity)
      .filter((incident) => status === "all" || incident.status === status)
      .filter((incident) => projectId === "all" || incident.project_id === Number(projectId));
  }, [incidentsQuery.data, projectById, projectId, search, severity, status]);
  const severityOptions = useMemo(() => [...new Set((incidentsQuery.data ?? []).map((incident) => incident.severity))].sort(), [incidentsQuery.data]);
  const statusOptions = useMemo(() => [...new Set((incidentsQuery.data ?? []).map((incident) => incident.status))].sort(), [incidentsQuery.data]);

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Response" title="Incidents" description="Track production incidents and begin AI-assisted investigations." actions={<Button onClick={() => setIsCreateDialogOpen(true)}>Create incident</Button>} />

      <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900">
        <strong>Backend security limitation:</strong> the current incidents-list endpoint returns records without server-side ownership filtering. This screen only renders incidents associated with projects returned for your account, but the backend endpoint must be fixed before it can be considered tenant-safe.
      </div>

      {incidentsQuery.isLoading || projectsQuery.isLoading ? <div className="space-y-3"><LoadingSkeleton className="h-10 w-full" /><LoadingSkeleton className="h-72 w-full" /></div> : null}
      {incidentsQuery.isError ? <ErrorState title="Unable to load incidents" description={incidentsQuery.error instanceof Error ? incidentsQuery.error.message : "Unable to load incidents."} onRetry={() => { void incidentsQuery.refetch(); }} /> : null}
      {projectsQuery.isError ? <ErrorState title="Unable to verify project access" description={projectsQuery.error instanceof Error ? projectsQuery.error.message : "Projects could not be loaded, so incidents cannot be safely scoped for display."} onRetry={() => { void projectsQuery.refetch(); }} /> : null}

      {!incidentsQuery.isLoading && !projectsQuery.isLoading && !incidentsQuery.isError && !projectsQuery.isError ? (
        <>
          <div className="grid gap-3 rounded-xl border bg-surface p-4 md:grid-cols-4">
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search title or description" className="h-10 rounded-lg border bg-surface px-3 text-sm outline-none focus:border-accent focus:ring-3 focus:ring-blue-100 md:col-span-1" />
            <select value={severity} onChange={(event) => setSeverity(event.target.value)} className="h-10 rounded-lg border bg-surface px-3 text-sm outline-none focus:border-accent"><option value="all">All severities</option>{severityOptions.map((option) => <option key={option} value={option}>{option}</option>)}</select>
            <select value={status} onChange={(event) => setStatus(event.target.value)} className="h-10 rounded-lg border bg-surface px-3 text-sm outline-none focus:border-accent"><option value="all">All statuses</option>{statusOptions.map((option) => <option key={option} value={option}>{option}</option>)}</select>
            <select value={projectId} onChange={(event) => setProjectId(event.target.value)} className="h-10 rounded-lg border bg-surface px-3 text-sm outline-none focus:border-accent"><option value="all">All projects</option>{projectsQuery.data?.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select>
          </div>

          {visibleIncidents.length === 0 ? <EmptyState title="No incidents to show" description={incidentsQuery.data?.length ? "No safely scoped incidents match the current filters." : "Create an incident to begin an investigation."} action={!incidentsQuery.data?.length ? <Button onClick={() => setIsCreateDialogOpen(true)}>Create incident</Button> : undefined} /> : (
            <div className="overflow-x-auto rounded-xl border bg-surface"><table className="w-full min-w-230 text-left text-sm"><thead className="bg-surface-subtle text-xs uppercase tracking-wide text-muted"><tr><th className="p-4 font-medium">Incident</th><th className="p-4 font-medium">Project</th><th className="p-4 font-medium">Service</th><th className="p-4 font-medium">Severity</th><th className="p-4 font-medium">Status</th><th className="p-4 font-medium">Created</th></tr></thead><tbody>{visibleIncidents.map((incident) => <tr key={incident.id} className="border-t transition hover:bg-surface-subtle"><td className="p-4"><Link href={`/incidents/${incident.id}`} className="font-medium text-foreground hover:text-accent"><span className="block">{incident.title}</span><span className="mt-1 block text-xs text-muted">{incident.external_id}</span></Link></td><td className="p-4 text-muted">{projectById.get(incident.project_id)}</td><td className="p-4 text-muted">{incident.service}</td><td className="p-4"><Badge tone={incident.severity.toLowerCase() === "critical" ? "danger" : incident.severity.toLowerCase() === "high" ? "warning" : "info"}>{incident.severity}</Badge></td><td className="p-4"><StatusBadge status={incident.status} /></td><td className="whitespace-nowrap p-4 text-muted">{new Date(incident.created_at).toLocaleDateString()}</td></tr>)}</tbody></table></div>
          )}
        </>
      ) : null}
      {isCreateDialogOpen ? <CreateIncidentDialog onClose={() => setIsCreateDialogOpen(false)} /> : null}
    </div>
  );
}
