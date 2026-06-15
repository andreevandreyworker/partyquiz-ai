import httpx

from app.config import settings
from app.exceptions import AIUnavailableError
from app.prompts import SYSTEM, build_user_prompt


class LLMService:
    async def suggest_question(
        self, draft: str, language: str
    ) -> str:
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": build_user_prompt(draft, language),
                },
            ],
            "max_tokens": 200,
            "temperature": 0.9,
        }
        headers = {"Content-Type": "application/json"}
        if settings.ai_api_key:
            headers["Authorization"] = f"Bearer {settings.ai_api_key}"
        try:
            async with httpx.AsyncClient(
                timeout=settings.ai_timeout
            ) as client:
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
