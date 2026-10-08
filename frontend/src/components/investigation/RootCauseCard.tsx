import type {
  RootCause,
} from "@/types/investigation";

type Props = {
  rootCause: RootCause | null;
};

export default function RootCauseCard({
  rootCause,
}: Props) {
  if (!rootCause) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
        <p className="text-sm text-zinc-500">
          Root cause analysis has not completed yet.
        </p>
      </div>
    );
  }

  const confidence =
    Math.round(rootCause.confidence * 100);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
            Root Cause
          </p>

          <h2 className="mt-2 text-lg font-semibold text-zinc-100">
            {rootCause.root_cause}
          </h2>
        </div>

        <div className="text-right">
          <p className="text-xs text-zinc-500">
            Model confidence
          </p>

          <p className="mt-1 text-xl font-semibold text-emerald-400">
            {confidence}%
          </p>
        </div>
      </div>

      <p className="mt-5 text-sm leading-6 text-zinc-400">
        {rootCause.explanation}
      </p>

      <div className="mt-5">
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
          Supporting evidence
        </p>

        <div className="mt-2 flex flex-wrap gap-2">
          {rootCause.evidence_ids.map(
            (id) => (
              <span
                key={id}
                className="rounded-md border border-zinc-700 bg-zinc-800 px-2 py-1 font-mono text-xs text-zinc-300"
              >
                Evidence #{id}
              </span>
            )
          )}
        </div>
      </div>

      {rootCause.uncertainty && (
        <div className="mt-5 rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
          <p className="text-xs font-medium text-amber-400">
            Uncertainty
          </p>

          <p className="mt-1 text-xs leading-5 text-zinc-400">
            {rootCause.uncertainty}
          </p>
        </div>
      )}
    </div>
  );
}