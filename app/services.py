import httpx

from app import aiconfig
from app.config import settings
from app.exceptions import AIUnavailableError


class LLMService:
    async def suggest_question(
        self, draft: str, language: str
    ) -> str:
        system, user = await aiconfig.get_prompt(draft, language)
        payload = {
            "model": await aiconfig.get_str(
                "ai_model", settings.ai_model
            ),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": await aiconfig.get_int("ai_max_tokens", 200),
            "temperature": await aiconfig.get_float(
                "ai_temperature", 0.9
            ),
        }
        headers = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"
        timeout = await aiconfig.get_float(
            "ai_timeout", settings.ai_timeout
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{settings.ai_base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception:
            raise AIUnavailableError()
        return data["choices"][0]["message"]["content"].strip()
