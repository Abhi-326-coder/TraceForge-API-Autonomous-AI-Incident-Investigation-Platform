from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.schemas.event import InvestigationEvent
from app.services.event_service import InvestigationEventService


def test_graph_event_id_is_appended_and_published_only_once():
    service = InvestigationEventService()
    service.redis = MagicMock()
    service.redis.eval.side_effect = [1, 0]
    event = InvestigationEvent(
        event_type="agent_started",
        investigation_id=44,
        message="Log Agent started.",
        agent="log_agent",
        data={},
        timestamp=datetime.now(timezone.utc),
        event_id="stable-node-event-key",
    )

    service.publish(event)
    service.publish(event)

    assert service.redis.eval.call_count == 2
    service.redis.publish.assert_called_once()
    assert service.redis.rpush.call_count == 0


def test_legacy_event_without_id_keeps_existing_publish_behavior():
    service = InvestigationEventService()
    service.redis = MagicMock()
    event = InvestigationEvent(
        event_type="manual_event",
        investigation_id=45,
        message="Existing event format",
        data={},
        timestamp=datetime.now(timezone.utc),
    )

    service.publish(event)

    service.redis.rpush.assert_called_once()
    service.redis.expire.assert_called_once()
    service.redis.publish.assert_called_once()
    service.redis.eval.assert_not_called()
