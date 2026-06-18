from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import aiconfig, ratelimit
from app.controllers import AIController
from app.dto import SuggestRequest, SuggestResponse
from app.exceptions import RateLimitError
from app.services import LLMService

router = APIRouter()
bearer = HTTPBearer(auto_error=False)


def get_controller() -> AIController:
    return AIController(LLMService())


@router.post("/suggest", response_model=SuggestResponse)
async def suggest(
    data: SuggestRequest,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    controller: AIController = Depends(get_controller),
) -> SuggestResponse:
    token = creds.credentials if creds else ""
    user_id = ratelimit.user_from_token(token)
    if user_id:
        limit = await aiconfig.get_int("ai_rate_limit", 10)
        window = await aiconfig.get_int("ai_rate_window_sec", 60)
        if not await ratelimit.allowed(user_id, limit, window):
            raise RateLimitError()
    return await controller.suggest(data)
