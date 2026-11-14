import { EmptyState } from "@/components/ui/States";
import { PageHeader } from "@/components/ui/PageHeader";

export default function SettingsPage() {
  return <div className="space-y-8"><PageHeader eyebrow="Workspace" title="Settings" description="Manage your TraceForge workspace preferences and integrations." /><EmptyState title="Settings are coming soon" description="Workspace configuration will be added as the integration experience is built." /></div>;
}
