import type {
  InvestigationEvent,
} from "@/types/investigation";

export type InvestigationStreamStatus = "connecting" | "connected" | "error";

export type InvestigationStreamOptions = {
  onStatus?: (status: InvestigationStreamStatus) => void;
  onError?: (message: string) => void;
};

export function parseInvestigationEvent(payload: string): InvestigationEvent {
  const event: unknown = JSON.parse(payload);
  if (!event || typeof event !== "object" || Array.isArray(event)) {
    throw new Error("Event payload must be a JSON object.");
  }
  const item = event as Record<string, unknown>;
  if (typeof item.event_type !== "string" || typeof item.investigation_id !== "number" || typeof item.message !== "string" ||
    typeof item.timestamp !== "string" || (item.agent !== undefined && item.agent !== null && typeof item.agent !== "string") ||
    !item.data || typeof item.data !== "object" || Array.isArray(item.data)) throw new Error("Invalid investigation event.");
  return item as unknown as InvestigationEvent;
}

export function investigationEventKey(event: InvestigationEvent) {
  return JSON.stringify([event.event_type, event.investigation_id, event.timestamp, event.message, event.agent ?? null, event.data]);
}

export function appendUniqueInvestigationEvent(events: InvestigationEvent[], event: InvestigationEvent) {
  const key = investigationEventKey(event);
  if (events.some((current) => investigationEventKey(current) === key)) return events;
  return [...events, event].sort((a, b) => Date.parse(a.timestamp) - Date.parse(b.timestamp));
}

export function connectInvestigationEvents(
  investigationId: number,
  onEvent: (
    event: InvestigationEvent
  ) => void,
  options: InvestigationStreamOptions = {},
) {
  options.onStatus?.("connecting");
  const source = new EventSource(
    `/api/backend/api/incidents/${investigationId}/events`
  );
  let closed = false;

  source.onopen = () => options.onStatus?.("connected");
  source.onerror = () => {
    if (closed) return;
    source.close();
    options.onStatus?.("error");
    options.onError?.("Live investigation updates disconnected. Reconnect to continue receiving events.");
  };

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

        try {
          onEvent(parseInvestigationEvent(message.data));
          options.onStatus?.("connected");
        } catch {
          options.onStatus?.("error");
          options.onError?.("Received an invalid live investigation event. Reconnect to resume updates.");
        }
      }
    );
  });

  return () => {
    closed = true;
    source.close();
  };
}
