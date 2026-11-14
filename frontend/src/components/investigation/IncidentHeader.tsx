type Props = {
  incident: {
    external_id: string;
    title: string;
    description: string;
    service: string;
    severity: string;
    status: string;
  };
};

export default function IncidentHeader({
  incident,
}: Props) {
  return (
    <div className="border-b pb-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            {incident.external_id}
          </p>

          <h1 className="mt-2 text-2xl font-semibold text-foreground">
            {incident.title}
          </h1>
        </div>

        <span className="rounded-md border border-red-200 bg-red-50 px-3 py-1 text-xs font-medium text-red-700">
          {incident.severity}
        </span>
      </div>

      <p className="mt-4 max-w-3xl text-sm leading-6 text-muted">
        {incident.description}
      </p>

      <div className="mt-4 flex gap-6 text-xs text-muted">
        <span>
          Service:{" "}
          <span className="text-foreground">
            {incident.service}
          </span>
        </span>

        <span>
          Status:{" "}
          <span className="text-foreground">
            {incident.status}
          </span>
        </span>
      </div>
    </div>
  );
}
