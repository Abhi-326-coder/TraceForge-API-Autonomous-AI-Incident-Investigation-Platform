from unittest.mock import MagicMock

from app.services.outbox_service import create_outbox_event


def test_create_outbox_event():
    db = MagicMock()

    event = create_outbox_event(
        db,
        event_type="INVESTIGATION_REQUESTED",
        aggregate_type="Investigation",
        aggregate_id="123",
        idempotency_key="investigation-created-123",
        payload={"investigation_id": 123},
    )

    assert event.event_type == "INVESTIGATION_REQUESTED"
    assert event.aggregate_id == "123"
    assert event.status == "PENDING"
    assert event.payload["investigation_id"] == 123

    db.add.assert_called_once_with(event)

    # The service must not commit independently.
    db.commit.assert_not_called()