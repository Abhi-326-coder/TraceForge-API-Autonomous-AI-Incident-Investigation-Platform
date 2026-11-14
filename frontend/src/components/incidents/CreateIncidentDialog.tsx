"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useCreateIncidentMutation } from "@/hooks/use-investigations";
import { useProjects } from "@/hooks/use-projects";
import { validateIncident, type IncidentFormErrors } from "@/lib/incident-validation";

type CreateIncidentDialogProps = { onClose: () => void };

export function CreateIncidentDialog({ onClose }: CreateIncidentDialogProps) {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [service, setService] = useState("");
  const [severity, setSeverity] = useState("");
  const [errors, setErrors] = useState<IncidentFormErrors>({});
  const { data: projects, isLoading: areProjectsLoading, isError: projectsError } = useProjects();
  const createIncident = useCreateIncidentMutation();

  function clearError(field: keyof IncidentFormErrors) {
    setErrors((current) => ({ ...current, [field]: undefined }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = { projectId, title: title.trim(), description: description.trim(), service: service.trim(), severity };
    const nextErrors = validateIncident(input);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length || !projectId) return;

    createIncident.mutate({ projectId, input: { title: input.title, description: input.description, service: input.service, severity: input.severity } }, { onSuccess: onClose });
  }

  const disabled = createIncident.isPending || areProjectsLoading || Boolean(projectsError) || !projects?.length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/30 p-4" role="presentation">
      <div className="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-xl border bg-surface p-6 shadow-xl" role="dialog" aria-modal="true" aria-labelledby="create-incident-title">
        <div className="flex items-start justify-between gap-4">
          <div><h2 id="create-incident-title" className="text-lg font-semibold text-foreground">Create incident</h2><p className="mt-1 text-sm text-muted">Record an incident for one of your projects.</p></div>
          <Button variant="ghost" size="sm" onClick={onClose} disabled={createIncident.isPending}>Close</Button>
        </div>
        <form className="mt-6 grid gap-5 sm:grid-cols-2" onSubmit={handleSubmit}>
          <label className="block sm:col-span-2"><span className="mb-2 block text-sm font-medium text-foreground">Project</span><select value={projectId ?? ""} disabled={disabled} onChange={(event) => { setProjectId(event.target.value ? Number(event.target.value) : null); clearError("projectId"); }} aria-invalid={Boolean(errors.projectId)} className="h-10 w-full rounded-lg border bg-surface px-3 text-sm text-foreground outline-none transition focus:border-accent focus:ring-3 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-surface-subtle"><option value="">{areProjectsLoading ? "Loading projects…" : "Select a project"}</option>{projects?.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select>{projectsError ? <span className="mt-1.5 block text-xs text-danger">Unable to load projects. Close the dialog and try again.</span> : null}{!areProjectsLoading && !projectsError && projects?.length === 0 ? <span className="mt-1.5 block text-xs text-danger">Create a project before creating an incident.</span> : null}{errors.projectId ? <span className="mt-1.5 block text-xs text-danger">{errors.projectId}</span> : null}</label>
          <label className="block sm:col-span-2"><span className="mb-2 block text-sm font-medium text-foreground">Title</span><Input value={title} disabled={createIncident.isPending} onChange={(event) => { setTitle(event.target.value); clearError("title"); }} aria-invalid={Boolean(errors.title)} />{errors.title ? <span className="mt-1.5 block text-xs text-danger">{errors.title}</span> : null}</label>
          <label className="block sm:col-span-2"><span className="mb-2 block text-sm font-medium text-foreground">Description</span><textarea value={description} disabled={createIncident.isPending} onChange={(event) => { setDescription(event.target.value); clearError("description"); }} rows={4} aria-invalid={Boolean(errors.description)} className="w-full rounded-lg border bg-surface px-3 py-2 text-sm text-foreground outline-none transition focus:border-accent focus:ring-3 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-surface-subtle" />{errors.description ? <span className="mt-1.5 block text-xs text-danger">{errors.description}</span> : null}</label>
          <label className="block"><span className="mb-2 block text-sm font-medium text-foreground">Service</span><Input value={service} disabled={createIncident.isPending} onChange={(event) => { setService(event.target.value); clearError("service"); }} aria-invalid={Boolean(errors.service)} />{errors.service ? <span className="mt-1.5 block text-xs text-danger">{errors.service}</span> : null}</label>
          <label className="block"><span className="mb-2 block text-sm font-medium text-foreground">Severity</span><select value={severity} disabled={createIncident.isPending} onChange={(event) => { setSeverity(event.target.value); clearError("severity"); }} aria-invalid={Boolean(errors.severity)} className="h-10 w-full rounded-lg border bg-surface px-3 text-sm text-foreground outline-none transition focus:border-accent focus:ring-3 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-surface-subtle"><option value="">Select severity</option><option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option><option value="CRITICAL">Critical</option></select>{errors.severity ? <span className="mt-1.5 block text-xs text-danger">{errors.severity}</span> : null}</label>
          {createIncident.isError ? <p className="sm:col-span-2 text-sm text-danger" role="alert">{createIncident.error instanceof Error ? createIncident.error.message : "Unable to create the incident."}</p> : null}
          <div className="flex justify-end gap-3 border-t pt-5 sm:col-span-2"><Button variant="secondary" onClick={onClose} disabled={createIncident.isPending}>Cancel</Button><Button type="submit" disabled={disabled}>{createIncident.isPending ? "Creating incident…" : "Create incident"}</Button></div>
        </form>
      </div>
    </div>
  );
}
