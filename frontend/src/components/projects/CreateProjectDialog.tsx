"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useCreateProjectMutation } from "@/hooks/use-projects";
import { validateProject } from "@/lib/project-validation";

type CreateProjectDialogProps = {
  onClose: () => void;
};

export function CreateProjectDialog({ onClose }: CreateProjectDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [nameError, setNameError] = useState<string | undefined>();
  const createProject = useCreateProjectMutation();

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input = { name: name.trim(), description: description.trim() || undefined };
    const errors = validateProject(input);
    setNameError(errors.name);
    if (errors.name) return;

    createProject.mutate(input, { onSuccess: onClose });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/30 p-4" role="presentation">
      <div className="w-full max-w-lg rounded-xl border bg-surface p-6 shadow-xl" role="dialog" aria-modal="true" aria-labelledby="create-project-title">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id="create-project-title" className="text-lg font-semibold text-foreground">Create project</h2>
            <p className="mt-1 text-sm text-muted">Add a workspace for the services TraceForge investigates.</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} disabled={createProject.isPending}>Close</Button>
        </div>

        <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-foreground">Project name</span>
            <Input value={name} onChange={(event) => { setName(event.target.value); setNameError(undefined); }} aria-invalid={Boolean(nameError)} aria-describedby={nameError ? "project-name-error" : undefined} autoFocus disabled={createProject.isPending} />
            {nameError ? <span id="project-name-error" className="mt-1.5 block text-xs text-danger">{nameError}</span> : null}
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-foreground">Description <span className="font-normal text-muted">(optional)</span></span>
            <textarea value={description} onChange={(event) => setDescription(event.target.value)} disabled={createProject.isPending} rows={4} className="w-full rounded-lg border bg-surface px-3 py-2 text-sm text-foreground outline-none transition focus:border-accent focus:ring-3 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-surface-subtle" />
          </label>
          {createProject.isError ? <p className="text-sm text-danger" role="alert">{createProject.error instanceof Error ? createProject.error.message : "Unable to create the project."}</p> : null}
          <div className="flex justify-end gap-3 border-t pt-5">
            <Button variant="secondary" onClick={onClose} disabled={createProject.isPending}>Cancel</Button>
            <Button type="submit" disabled={createProject.isPending}>{createProject.isPending ? "Creating project…" : "Create project"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
