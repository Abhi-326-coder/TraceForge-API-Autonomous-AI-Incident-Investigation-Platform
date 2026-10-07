## Add the Event service, bus and route

- What we are implementing is to show the user at what stage there Investigation is with timeline 
- Like "Supervisor completed the planning", showing the user 

### Creating a schema for Event function

```python
class InvestigationEvent(BaseModel):

    event_type: str

    investigation_id: int

    message: str

    agent: str | None = None

    data: dict[str, Any] = {}

    timestamp: datetime
```
- An example :
```json
{
  "event_type": "agent_started",
  "investigation_id": 1,
  "message": "Log Agent started",
  "agent": "log_agent",
  "data": {},
  "timestamp": "2026-10-08T01:10:00"
}
```
### Add the event_service for the event and for now it is not storing in any database but local works for development
```python
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
    
```

### Add the Event bus having the object of the event service

```python
from app.services.event_service import (
    InvestigationEventService,
)


event_service = InvestigationEventService()
```

- Adding the event service onto the nodes of the graph by just ``event_service.publish()`` in nodes.py

- Create the route of /event with StreamingResponse ``from fastapi.responses import StreamingResponse``

```python
@router.get(
    "/{investigation_id}/events"
)
async def investigation_events(
    investigation_id: int,
):

    async def event_stream():

        sent = 0

        while True:

            events = event_service.get_events(
                investigation_id
            )

            while sent < len(events):

                event = events[sent]

                payload = (
                    event.model_dump_json()
                )

                yield (
                    f"event: {event.event_type}\n"
                    f"data: {payload}\n\n"
                )

                sent += 1

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```
