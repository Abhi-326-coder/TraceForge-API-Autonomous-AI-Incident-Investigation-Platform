import type {
  InvestigationEvent,
} from "@/types/investigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export function connectInvestigationEvents(
  investigationId: number,
  onEvent: (
    event: InvestigationEvent
  ) => void
) {
  const source = new EventSource(
    `${API_URL}/api/investigations/${investigationId}/events`
  );

  const eventTypes = [
    "investigation_started",
    "supervisor_started",
    "supervisor_completed",
    "agent_started",
    "agent_completed",
    "tool_called",
    "tool_completed",
    "evidence_collected",
    "root_cause_started",
    "root_cause_completed",
    "investigation_completed",
    "investigation_failed",
  ];

  eventTypes.forEach((eventType) => {
    source.addEventListener(
      eventType,
      (event) => {
        const message =
          event as MessageEvent;

        const data =
          JSON.parse(message.data);

        onEvent(data);
      }
    );
  });

  return () => {
    source.close();
  };
}