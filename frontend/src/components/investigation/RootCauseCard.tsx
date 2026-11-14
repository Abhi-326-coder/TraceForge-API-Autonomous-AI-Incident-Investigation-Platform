import type {
  RootCause,
} from "@/types/investigation";

type Props = {
  rootCause: RootCause | null;
  onEvidenceClick?: (evidenceId: number) => void;
};

export default function RootCauseCard({
  rootCause,
  onEvidenceClick,
}: Props) {
  if (!rootCause) {
    return (
      <div className="rounded-xl border bg-surface p-6">
        <p className="text-sm text-muted">
          Root cause analysis has not completed yet.
        </p>
      </div>
    );
  }

  const confidence =
    Math.round(rootCause.confidence * 100);

  return (
    <div className="rounded-xl border bg-surface p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-muted">
            Root Cause
          </p>

          <h2 className="mt-2 text-lg font-semibold text-foreground">
            {rootCause.root_cause}
          </h2>
        </div>

        <div className="text-right">
          <p className="text-xs text-muted">
            Model confidence
          </p>

          <p className="mt-1 text-xl font-semibold text-emerald-400">
            {confidence}%
          </p>
        </div>
      </div>

      <p className="mt-5 text-sm leading-6 text-muted">
        {rootCause.explanation}
      </p>

      <div className="mt-5">
        <p className="text-xs font-medium uppercase tracking-wider text-muted">
          Supporting evidence
        </p>

        <div className="mt-2 flex flex-wrap gap-2">
          {rootCause.evidence_ids.map(
            (id) => (
              <button type="button" onClick={() => onEvidenceClick?.(id)}
                key={id}
                className="rounded-md border bg-surface-subtle px-2 py-1 font-mono text-xs text-foreground"
              >
                Evidence #{id}
              </button>
            )
          )}
        </div>
      </div>

      {rootCause.uncertainty && (
        <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <p className="text-xs font-medium text-amber-700">
            Uncertainty
          </p>

          <p className="mt-1 text-xs leading-5 text-amber-800">
            {rootCause.uncertainty}
          </p>
        </div>
      )}
    </div>
  );
}
