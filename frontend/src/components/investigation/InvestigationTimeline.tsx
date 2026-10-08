"use client";

import type {
  InvestigationEvent,
} from "@/types/investigation";

type Props = {
  events: InvestigationEvent[];
};

export default function InvestigationTimeline({
  events,
}: Props) {
  return (
    <div className="space-y-5">
      {events.map((event, index) => (
        <div
          key={`${event.timestamp}-${index}`}
          className="flex gap-4"
        >
          <div className="flex flex-col items-center">
            <div className="h-3 w-3 rounded-full bg-emerald-400" />

            {index !== events.length - 1 && (
              <div className="mt-2 h-full w-px bg-zinc-800" />
            )}
          </div>

          <div className="pb-4">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-zinc-100">
                {event.message}
              </span>

              <span className="text-xs text-zinc-500">
                {new Date(
                  event.timestamp
                ).toLocaleTimeString()}
              </span>
            </div>

            {event.agent && (
              <p className="mt-1 text-xs text-zinc-500">
                {event.agent}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}