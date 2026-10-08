"use client";

import {
  useEffect,
  useState,
} from "react";

import IncidentHeader from "@/components/investigation/IncidentHeader";
import InvestigationTimeline from "@/components/investigation/InvestigationTimeline";
import EvidencePanel from "@/components/investigation/EvidencePanel";
import RootCauseCard from "@/components/investigation/RootCauseCard";

import {
  connectInvestigationEvents,
} from "@/lib/sse";

import type {
  InvestigationEvent,
  Evidence,
  RootCause,
} from "@/types/investigation";

type Props = {
  params: Promise<{
    incidentId: string;
  }>;
};

export default function IncidentPage({
  params,
}: Props) {
  const [events, setEvents] = useState<
    InvestigationEvent[]
  >([]);

  const [evidence, setEvidence] =
    useState<Evidence[]>([]);

  const [rootCause, setRootCause] =
    useState<RootCause | null>(null);

  const [incident, setIncident] =
    useState<any>(null);

  const [investigationId, setInvestigationId] =
    useState<number | null>(null);

  useEffect(() => {
    async function load() {
      const { incidentId } =
        await params;

      const response = await fetch(
        `http://localhost:8000/api/incidents/${incidentId}`
      );

      const data =
        await response.json();

      setIncident(data);

      // Temporary:
      // use the latest investigation.
      const investigationResponse =
        await fetch(
          `http://localhost:8000/api/incidents/${incidentId}/investigations`
        );

      const investigations =
        await investigationResponse.json();

      if (investigations.length > 0) {
        setInvestigationId(
          investigations[
            investigations.length - 1
          ].id
        );
      }
    }

    load();
  }, [params]);

  useEffect(() => {
    if (!investigationId) {
      return;
    }

    return connectInvestigationEvents(
      investigationId,
      (event) => {
        setEvents((current) => [
          ...current,
          event,
        ]);

        if (
          event.event_type ===
            "root_cause_completed"
        ) {
          const result =
            event.data;

          setRootCause(
            result as unknown as RootCause
          );
        }
      }
    );
  }, [investigationId]);

  if (!incident) {
    return (
      <main className="min-h-screen bg-zinc-950 p-10 text-zinc-400">
        Loading incident...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-[1600px] px-8 py-8">

        <IncidentHeader
          incident={incident}
        />

        <div className="mt-8 grid grid-cols-12 gap-6">

          <section className="col-span-7 rounded-xl border border-zinc-800 bg-zinc-950 p-6">

            <div className="mb-6">
              <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                Investigation
              </p>

              <h2 className="mt-1 text-lg font-semibold">
                Live investigation timeline
              </h2>
            </div>

            <InvestigationTimeline
              events={events}
            />

          </section>

          <aside className="col-span-5 space-y-6">

            <section>
              <div className="mb-3">
                <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                  Root Cause
                </p>
              </div>

              <RootCauseCard
                rootCause={rootCause}
              />
            </section>

            <section>
              <div className="mb-3">
                <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                  Evidence
                </p>
              </div>

              <EvidencePanel
                evidence={evidence}
              />
            </section>

          </aside>

        </div>
      </div>
    </main>
  );
}