"use client";

import Link from "next/link";
import { use } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState, ErrorState, LoadingSkeleton } from "@/components/ui/States";
import { useProjects } from "@/hooks/use-projects";
import { PageHeader } from "@/components/ui/PageHeader";

type Props = { params: Promise<{ projectId: string }> };

export default function ProjectDetailsPage({ params }: Props) {
  const { projectId: projectIdParam } = use(params);
  const projectId = Number(projectIdParam);
  const { data: projects, isLoading, isError, error, refetch } = useProjects();
  const project = Number.isInteger(projectId) ? projects?.find((item) => item.id === projectId) : undefined;

  if (isLoading) return <LoadingSkeleton className="h-56 w-full" />;
  if (isError) return <ErrorState title="Unable to load project" description={error instanceof Error ? error.message : "Unable to load this project."} onRetry={() => { void refetch(); }} />;
  if (!project) {
    return <EmptyState title="Project not found" description="This project is unavailable or you no longer have access to it." action={<Link href="/projects"><Button variant="secondary">Back to projects</Button></Link>} />;
  }

  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Workspace project" title={project.name} description="Project information available through the current projects API." actions={<Link href="/projects"><Button variant="secondary">Back to projects</Button></Link>} />
      <Card className="max-w-3xl p-6">
        <dl className="space-y-6">
          <div>
            <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">Description</dt>
            <dd className="mt-2 text-sm leading-6 text-foreground">{project.description || "No description provided."}</dd>
          </div>
          <div className="border-t pt-6">
            <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-muted">Created</dt>
            <dd className="mt-2 text-sm text-foreground">{new Date(project.created_at).toLocaleString()}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
