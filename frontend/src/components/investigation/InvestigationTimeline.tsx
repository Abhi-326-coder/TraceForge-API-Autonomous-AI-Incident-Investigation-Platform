"use client";

import type {
  InvestigationEvent,
} from "@/types/investigation";
import { timelineEventDetails } from "@/lib/investigation-presenters";

type Props = {
  events: InvestigationEvent[];
  onEvidenceClick?: (evidenceId: number) => void;
};

export default function InvestigationTimeline({
  events,
  onEvidenceClick,
}: Props) {
  return (
    <div className="space-y-5">
      {events.map((event, index) => {
        const { stage, evidenceIds } = timelineEventDetails(event);
        return (
        <div
          key={`${event.timestamp}-${index}`}
          className="flex gap-4"
        >
          <div className="flex flex-col items-center">
            <div className="h-3 w-3 rounded-full bg-emerald-400" />

            {index !== events.length - 1 && (
              <div className="mt-2 h-full w-px bg-border" />
            )}
          </div>

          <div className="pb-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-sm font-medium text-foreground">
                {event.message}
              </span>
              <span className="rounded bg-surface-subtle px-1.5 py-0.5 font-mono text-[11px] text-muted">{event.event_type}</span>
              <span className="text-xs text-muted">
                {new Date(
                  event.timestamp
                ).toLocaleTimeString()}
              </span>
            </div>

            {event.agent && (
              <p className="mt-1 text-xs text-muted">
                {event.agent}
              </p>
            )}
            {stage ? <p className="mt-1 text-xs text-muted">Stage: {stage}</p> : null}
            {evidenceIds.length ? <div className="mt-2 flex flex-wrap gap-2">{evidenceIds.map((evidenceId) => <button key={evidenceId} type="button" onClick={() => onEvidenceClick?.(evidenceId)} className="text-xs font-medium text-accent hover:underline">Evidence #{evidenceId}</button>)}</div> : null}
          </div>
        </div>
        );
      })}
    </div>
  );
}
