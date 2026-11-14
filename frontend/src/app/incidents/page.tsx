import { EmptyState } from "@/components/ui/States";
import { PageHeader } from "@/components/ui/PageHeader";

export default function IncidentsPage() {
  return (
    <div className="space-y-8">
      <PageHeader eyebrow="Response" title="Incidents" description="Track production incidents and begin AI-assisted investigations." />
      <EmptyState title="No incidents to show" description="Incident data will appear here once the authenticated incident integration is connected." />
    </div>
  );
}
