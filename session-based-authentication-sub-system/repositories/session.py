import json
import secrets
from typing import Any
from uuid import UUID

from core.config import Settings
from redis import Redis


class SessionRepository:
    def __init__(self, redis_client: Redis, settings: Settings) -> None:
        self.redis = redis_client
        self.settings = settings

    def _make_session_key(self, session_id: str) -> str:
        return f"{self.settings.session_prefix}{session_id}"

    def _make_user_sessions_key(self, user_id: UUID) -> str:
        return f"{self.settings.sessions_prefix}{user_id}"

    @staticmethod
    def _decode_member(value: str | bytes) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    def create_session(
        self,
        user_id: UUID,
        extra: dict[str, Any] | None = None,
    ) -> str:

        session_id: str = secrets.token_urlsafe(32)
        session_key: str = self._make_session_key(session_id)
        user_sessions_key: str = self._make_user_sessions_key(user_id)

        session_data = {
            **(extra or {}),
            "user_id": str(user_id),
        }

        serialized_data: str = json.dumps(session_data)

        with self.redis.pipeline(transaction=True) as pipe:
            pipe.set(
                name=session_key,
                value=serialized_data,
                ex=self.settings.session_expire_seconds,
            )

            pipe.sadd(user_sessions_key, session_id)

            pipe.execute()

        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        session_key: str = self._make_session_key(session_id)
        raw_data = self.redis.get(session_key)

        if raw_data is None:
            return None

        try:
            deserialized_data = json.loads(raw_data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.redis.delete(session_key)
            return None

        if not isinstance(deserialized_data, dict):
            self.redis.delete(session_key)
            return None

        return deserialized_data

    def delete_session(self, session_id: str) -> None:

        session_data: dict[str, Any] | None = self.get_session(session_id)

        user_id = None

        if session_data is not None:
            try:
                user_id = UUID(str(session_data["user_id"]))
            except (KeyError, TypeError, ValueError):
                pass

        with self.redis.pipeline(transaction=True) as pipe:

            pipe.delete(self._make_session_key(session_id))

            if user_id is not None:
                pipe.srem(
                    self._make_user_sessions_key(user_id),
                    session_id,
                )

            pipe.execute()

    def delete_all_sessions(self, user_id: UUID) -> None:
        user_sessions_key: str = self._make_user_sessions_key(user_id)

        session_ids: set[str] = {
            self._decode_member(value)
            for value in self.redis.smembers(user_sessions_key)
        }

        with self.redis.pipeline(transaction=True) as pipe:
            for session_id in session_ids:
                pipe.delete(self._make_session_key(session_id))

            pipe.delete(user_sessions_key)
            pipe.execute()

    def refresh_session_ttl(self, session_id: str) -> None:
        session_key: str = self._make_session_key(session_id)
        session_data: dict[str, Any] | None = self.get_session(session_id)

        if session_data is None:
            return

        ttl: int = self.settings.session_expire_seconds

        self.redis.expire(session_key, ttl)


    def get_all_user_sessions(self, user_id: UUID) -> set[str]:
        user_sessions_key: str = self._make_user_sessions_key(user_id)

        session_ids: list[str] = [
            self._decode_member(value)
            for value in self.redis.smembers(user_sessions_key)
        ]

        if not session_ids:
            return set()

        with self.redis.pipeline(transaction=False) as pipe:

            for session_id in session_ids:
                pipe.exists(self._make_session_key(session_id))

            existence_results = pipe.execute()

        active_sessions: set[str] = set()
        stale_sessions: set[str] = set()

        for session_id, exists in zip(session_ids, existence_results):
            if exists:
                active_sessions.add(session_id)
            else:
                stale_sessions.add(session_id)

        if stale_sessions:
            self.redis.srem(user_sessions_key, *stale_sessions)

        return active_sessions

    def delete_specific_session(self, user_id: UUID, session_id: str) -> bool:

        raw_data: dict[str, Any] | None = self.get_session(session_id)

        if raw_data is None:
            return False

        try:
            session_user_id = UUID(str(raw_data["user_id"]))
        except (KeyError, TypeError, ValueError):
            return False

        if session_user_id != user_id:
            return False

        user_sessions_key: str = self._make_user_sessions_key(user_id)

        with self.redis.pipeline(transaction=True) as pipe:

            pipe.delete(self._make_session_key(session_id))
            pipe.srem(user_sessions_key, session_id)

            pipe.execute()

        return True
