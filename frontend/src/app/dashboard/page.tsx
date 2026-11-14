import { PageHeader } from "@/components/ui/PageHeader";
import { EmptyState } from "@/components/ui/States";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Workspace"
        title="Overview"
        description="Monitor incidents, investigations, and remediation activity from one place."
      />
      <EmptyState
        title="Your workspace is ready"
        description="Connect projects and create incidents to begin building an investigation history."
      />
    </div>
  );
}
