import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.prompts import SYSTEM, build_user_prompt

_TTL = 60.0
_engine = (
    create_async_engine(settings.config_db_url, echo=False)
    if settings.config_db_url
    else None
)
_cache: dict[str, tuple[float, object]] = {}


def _fresh(key: str) -> object | None:
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < _TTL:
        return hit[1]
    return None


def _store(key: str, value: object) -> object:
    _cache[key] = (time.monotonic(), value)
    return value


async def _prompts() -> dict[str, dict]:
    cached = _fresh("prompts")
    if cached is not None:
        return cached
    if _engine is None:
        return {}
    try:
        async with _engine.connect() as conn:
            rows = await conn.execute(
                text(
                    "SELECT lang, system, user_draft, user_fresh "
                    "FROM ai_prompts"
                )
            )
            data = {
                r.lang: {
                    "system": r.system,
                    "draft": r.user_draft,
                    "fresh": r.user_fresh,
                }
                for r in rows
            }
        return _store("prompts", data)
    except Exception:
        return {}


async def get_prompt(draft: str, language: str) -> tuple[str, str]:
    prompts = await _prompts()
    row = prompts.get(language)
    if not row or not row.get("system"):
        return SYSTEM, build_user_prompt(draft, language)
    draft = draft.strip()
    if draft:
        user = row["draft"].replace("{draft}", draft)
    else:
        user = row["fresh"]
    return row["system"], user


async def _config() -> dict[str, str]:
    cached = _fresh("config")
    if cached is not None:
        return cached
    if _engine is None:
        return {}
    try:
        async with _engine.connect() as conn:
            rows = await conn.execute(
                text("SELECT key, value FROM app_config")
            )
            data = {r.key: r.value for r in rows}
        return _store("config", data)
    except Exception:
        return {}


async def get_str(key: str, default: str) -> str:
    return (await _config()).get(key) or default


async def get_float(key: str, default: float) -> float:
    raw = (await _config()).get(key)
    try:
        return float(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default


async def get_int(key: str, default: int) -> int:
    raw = (await _config()).get(key)
    try:
        return int(raw) if raw is not None else default
    except (TypeError, ValueError):
        return default
