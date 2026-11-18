import json

import redis
from redis.exceptions import RedisError

from app.config import settings
from app.schemas.event import InvestigationEvent


class InvestigationEventService:
    _APPEND_EVENT_IF_NEW = """
    if redis.call('SADD', KEYS[1], ARGV[1]) == 0 then
        return 0
    end
    redis.call('RPUSH', KEYS[2], ARGV[2])
    redis.call('EXPIRE', KEYS[1], ARGV[3])
    redis.call('EXPIRE', KEYS[2], ARGV[3])
    return 1
    """

    def __init__(self):
        self.redis = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
            health_check_interval=30,
        )

        self.event_ttl_seconds = 60 * 60 * 24  # 24 hours

    @staticmethod
    def _events_key(investigation_id: int) -> str:
        return f"traceforge:investigation:{investigation_id}:events"

    @staticmethod
    def _channel(investigation_id: int) -> str:
        return f"traceforge:investigation:{investigation_id}:live"

    @staticmethod
    def _event_ids_key(investigation_id: int) -> str:
        return f"traceforge:investigation:{investigation_id}:event-ids"

    def publish(self, event: InvestigationEvent) -> None:
        payload = event.model_dump_json()

        # Save the event first so clients can retrieve it later. Graph node
        # events carry deterministic IDs and are appended only once even if
        # LangGraph replays a node after a checkpoint failure.
        key = self._events_key(event.investigation_id)
        if event.event_id is not None:
            inserted = self.redis.eval(
                self._APPEND_EVENT_IF_NEW,
                2,
                self._event_ids_key(event.investigation_id),
                key,
                event.event_id,
                payload,
                self.event_ttl_seconds,
            )
            if not inserted:
                return
        else:
            self.redis.rpush(key, payload)
            self.redis.expire(key, self.event_ttl_seconds)

        # Notify currently connected subscribers.
        self.redis.publish(
            self._channel(event.investigation_id),
            payload,
        )

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

    def health_check(self) -> bool:
        return bool(self.redis.ping())
