import type {
    Evidence,
} from "@/types/investigation"

type Props = {
    evidence:Evidence[];
}

const sourceLabels: Record<
  string,
  string
> = {
  logs: "LOG",
  metrics: "METRIC",
  github: "GITHUB",
  knowledge: "RAG",
};

export default function EvidencePanel({
  evidence,
}: Props) {
  return (
    <div className="space-y-3">
      {evidence.map((item) => (
        <div
          key={item.id}
          className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-500">
              {sourceLabels[item.source_type] ||
                item.source_type.toUpperCase()}
            </span>

            <span className="font-mono text-xs text-zinc-600">
              #{item.id}
            </span>
          </div>

          <h3 className="mt-2 text-sm font-medium text-zinc-200">
            {item.title}
          </h3>

          <p className="mt-2 text-xs leading-5 text-zinc-400">
            {item.content}
          </p>
        </div>
      ))}
    </div>
  );
}