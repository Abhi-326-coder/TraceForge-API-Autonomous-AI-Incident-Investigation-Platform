import { EmptyState } from "@/components/ui/States";
import { PageHeader } from "@/components/ui/PageHeader";

export default function InvestigationsPage() {
  return <div className="space-y-8"><PageHeader eyebrow="Response" title="Investigations" description="Review active and completed autonomous investigations." /><EmptyState title="No investigations yet" description="Investigations are created from an incident when analysis begins." /></div>;
}
