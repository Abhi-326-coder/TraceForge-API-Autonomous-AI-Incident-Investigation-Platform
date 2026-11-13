import socket
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.schemas.event import InvestigationEvent
from app.services.event_service import InvestigationEventService


def _redis_available() -> bool:
    try:
        with socket.create_connection(("localhost", 6379), timeout=1):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _redis_available(),
    reason="Redis is not running on localhost:6379",
)


def test_event_is_stored_and_retrievable():
    service = InvestigationEventService()

    # Use a unique ID to avoid colliding with real investigations.
    investigation_id = 900_000 + int(uuid4().int % 99_999)

    event = InvestigationEvent(
        event_type="investigation_started",
        investigation_id=investigation_id,
        message="Test investigation started",
        agent=None,
        data={"test": True},
        timestamp=datetime.now(timezone.utc),
    )

    service.publish(event)

    events = service.get_events(investigation_id)

    assert len(events) == 1
    assert events[0].event_type == "investigation_started"
    assert events[0].data["test"] is True

    service.redis.delete(
        service._events_key(investigation_id)
    )