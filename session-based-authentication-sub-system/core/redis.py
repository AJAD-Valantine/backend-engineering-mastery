from core.config import get_settings
from redis import Redis

settings = get_settings()

redis_client = Redis.from_url(
    url=settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)
