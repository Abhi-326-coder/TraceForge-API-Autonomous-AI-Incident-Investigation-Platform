import redis

from app.config import settings


class InvestigationLockService:

    def __init__(self):
        self.redis = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )

    @staticmethod
    def get_lock_key(investigation_id: int) -> str:
        return f"traceforge:investigation:{investigation_id}:lock"

    def acquire(
        self,
        investigation_id: int,
        task_id: str,
        ttl_seconds: int = 900,
    ) -> bool:

        key = self.get_lock_key(investigation_id)

        result = self.redis.set(
            key,
            task_id,
            nx=True,
            ex=ttl_seconds,
        )

        return bool(result)

    def release(
        self,
        investigation_id: int,
        task_id: str,
    ) -> bool:

        key = self.get_lock_key(investigation_id)

        # Release only if this task owns the lock.
        script = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('DEL', KEYS[1])
        end
        return 0
        """

        result = self.redis.eval(
            script,
            1,
            key,
            task_id,
        )

        return bool(result)


investigation_lock_service = InvestigationLockService()