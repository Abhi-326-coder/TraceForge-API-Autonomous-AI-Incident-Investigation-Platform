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
    <div className="border-b border-zinc-800 pb-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
            {incident.external_id}
          </p>

          <h1 className="mt-2 text-2xl font-semibold text-zinc-100">
            {incident.title}
          </h1>
        </div>

        <span className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-400">
          {incident.severity}
        </span>
      </div>

      <p className="mt-4 max-w-3xl text-sm leading-6 text-zinc-400">
        {incident.description}
      </p>

      <div className="mt-4 flex gap-6 text-xs text-zinc-500">
        <span>
          Service:{" "}
          <span className="text-zinc-300">
            {incident.service}
          </span>
        </span>

        <span>
          Status:{" "}
          <span className="text-zinc-300">
            {incident.status}
          </span>
        </span>
      </div>
    </div>
  );
}