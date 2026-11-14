"use client";

import Link from "next/link";
import { useState } from "react";

import { CreateProjectDialog } from "@/components/projects/CreateProjectDialog";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState, ErrorState, LoadingSkeleton } from "@/components/ui/States";
import { useProjects } from "@/hooks/use-projects";
import { PageHeader } from "@/components/ui/PageHeader";

export default function ProjectsPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { data: projects, isLoading, isError, error, refetch } = useProjects();

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Workspace"
        title="Projects"
        description="Organize the services and connections that TraceForge investigates."
        actions={<Button onClick={() => setIsCreateDialogOpen(true)}>Create project</Button>}
      />

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((item) => <LoadingSkeleton key={item} className="h-44 w-full" />)}
        </div>
      ) : null}

      {isError ? (
        <ErrorState title="Unable to load projects" description={error instanceof Error ? error.message : "Unable to load your projects."} onRetry={() => { void refetch(); }} />
      ) : null}

      {!isLoading && !isError && projects?.length === 0 ? (
        <EmptyState title="No projects yet" description="Create a project to organize the services TraceForge investigates." action={<Button onClick={() => setIsCreateDialogOpen(true)}>Create project</Button>} />
      ) : null}

      {!isLoading && !isError && projects && projects.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {projects.map((project) => (
            <Link key={project.id} href={`/projects/${project.id}`} className="group focus:outline-none">
              <Card className="h-full p-5 transition group-hover:border-accent group-hover:shadow-sm group-focus-visible:border-accent group-focus-visible:ring-3 group-focus-visible:ring-blue-100">
                <div className="flex items-start justify-between gap-4">
                  <h2 className="text-base font-semibold text-foreground">{project.name}</h2>
                  <span className="rounded-md bg-accent-subtle px-2 py-1 text-xs font-medium text-accent">Project</span>
                </div>
                <p className="mt-3 line-clamp-3 min-h-15 text-sm leading-6 text-muted">{project.description || "No description provided."}</p>
                <p className="mt-5 border-t pt-4 text-xs text-muted">Created {new Date(project.created_at).toLocaleDateString()}</p>
              </Card>
            </Link>
          ))}
        </div>
      ) : null}

      {isCreateDialogOpen ? <CreateProjectDialog onClose={() => setIsCreateDialogOpen(false)} /> : null}
    </div>
  );
}
