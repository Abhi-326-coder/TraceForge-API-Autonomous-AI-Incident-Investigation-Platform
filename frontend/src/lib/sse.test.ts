import assert from "node:assert/strict";
import test from "node:test";

import { appendUniqueInvestigationEvent, connectInvestigationEvents, parseInvestigationEvent } from "./sse.ts";

class MockEventSource {
  static latest: MockEventSource | undefined;
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  closed = false;
  private readonly listeners = new Map<string, (event: { data: string }) => void>();

  readonly url: string;

  constructor(url: string) {
    this.url = url;
    MockEventSource.latest = this;
  }

  addEventListener(type: string, listener: (event: { data: string }) => void) {
    this.listeners.set(type, listener);
  }

  close() {
    this.closed = true;
  }

  emit(type: string, data: string) {
    this.listeners.get(type)?.({ data });
  }
}

test("SSE parser accepts event objects and rejects malformed payloads", () => {
  assert.equal(parseInvestigationEvent('{"event_type":"agent_started","investigation_id":1,"message":"Started","timestamp":"2026-01-01T00:00:00Z","data":{}}').event_type, "agent_started");
  assert.throws(() => parseInvestigationEvent("not json"));
  assert.throws(() => parseInvestigationEvent("[]"));
});

test("SSE connection reports malformed events and connection failures", () => {
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, "EventSource");
  Object.defineProperty(globalThis, "EventSource", { configurable: true, value: MockEventSource });
  const statuses: string[] = [];
  const errors: string[] = [];
  const received: string[] = [];

  const disconnect = connectInvestigationEvents(9, (event) => received.push(event.event_type), {
    onStatus: (status) => statuses.push(status),
    onError: (message) => errors.push(message),
  });
  const source = MockEventSource.latest!;
  assert.equal(source.url, "/api/backend/api/incidents/9/events");
  source.onopen?.();
  source.emit("agent_started", "not json");
  source.emit("agent_started", '{"event_type":"agent_started","investigation_id":9,"message":"Started","timestamp":"2026-01-01T00:00:00Z","data":{}}');
  source.onerror?.();

  assert.deepEqual(received, ["agent_started"]);
  assert.deepEqual(statuses, ["connecting", "connected", "error", "connected", "error"]);
  assert.equal(errors.length, 2);
  assert.equal(source.closed, true);
  disconnect();
  assert.equal(source.closed, true);
  if (descriptor) Object.defineProperty(globalThis, "EventSource", descriptor);
  else delete (globalThis as { EventSource?: unknown }).EventSource;
});

test("timeline events are deduplicated across reconnects and ordered by timestamp", () => {
  const later = { event_type: "agent_completed", investigation_id: 1, message: "Done", timestamp: "2026-01-01T00:01:00Z", data: {} };
  const earlier = { event_type: "agent_started", investigation_id: 1, message: "Started", timestamp: "2026-01-01T00:00:00Z", data: {} };
  const events = appendUniqueInvestigationEvent(appendUniqueInvestigationEvent([], later), earlier);
  assert.equal(appendUniqueInvestigationEvent(events, earlier).length, 2);
  assert.deepEqual(events.map((event) => event.event_type), ["agent_started", "agent_completed"]);
});
