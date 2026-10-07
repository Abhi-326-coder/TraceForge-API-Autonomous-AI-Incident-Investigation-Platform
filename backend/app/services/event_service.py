from datetime import datetime

from app.schemas.event import InvestigationEvent


class InvestigationEventService:

    def __init__(self):

        self.events: dict[
            int,
            list[InvestigationEvent]
        ] = {}

    def publish(
        self,
        investigation_id: int,
        event_type: str,
        message: str,
        agent: str | None = None,
        data: dict | None = None,
    ):

        event = InvestigationEvent(
            event_type=event_type,
            investigation_id=investigation_id,
            message=message,
            agent=agent,
            data=data or {},
            timestamp=datetime.utcnow(),
        )

        self.events.setdefault(
            investigation_id,
            [],
        ).append(event)

        return event

    def get_events(
        self,
        investigation_id: int,
    ):

        return self.events.get(
            investigation_id,
            [],
        )