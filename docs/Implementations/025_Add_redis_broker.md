## Connect the Redis 

### Add the Redis docker image in docker-compose.yml

```bash
redis:
    image: redis:7-alpine
    container_name: traceforge-redis
    ports:
      - "127.0.0.1:6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
```

- also Adding redis server in .env and config setting

```python
def publish(self, event: InvestigationEvent) -> None:
        payload = event.model_dump_json()

        # Save the event first so clients can retrieve it later.
        key = self._events_key(event.investigation_id)

        self.redis.rpush(key, payload)
        self.redis.expire(key, self.event_ttl_seconds)

        # Notify currently connected subscribers.
        self.redis.publish(
            self._channel(event.investigation_id),
            payload,
        )
```

```python
def get_events(
        self,
        investigation_id: int,
    ) -> list[InvestigationEvent]:
        payloads = self.redis.lrange(
            self._events_key(investigation_id),
            0,
            -1,
        )

        return [
            InvestigationEvent.model_validate_json(payload)
            for payload in payloads
        ]
```

- Event Bus 

```python
from app.services.event_service import InvestigationEventService

event_service = InvestigationEventService()
```