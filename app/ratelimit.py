import time

import jwt
import redis.asyncio as aioredis

from app.config import settings

_redis = (
    aioredis.from_url(settings.redis_url, decode_responses=True)
    if settings.redis_url
    else None
)


def user_from_token(token: str) -> str | None:
    if not token or not settings.jwt_secret:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        return None
    return payload.get("sub")


async def allowed(user_id: str, limit: int, window: int) -> bool:
    if _redis is None or limit <= 0:
        return True
    bucket = int(time.time()) // window
    key = f"ai_rl:{user_id}:{bucket}"
    try:
        count = await _redis.incr(key)
        if count == 1:
            await _redis.expire(key, window)
        return count <= limit
    except Exception:
        return True
