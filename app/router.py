from fastapi import APIRouter, Depends

from app.controllers import AIController
from app.dto import SuggestRequest, SuggestResponse
from app.services import LLMService

router = APIRouter()


def get_controller() -> AIController:
    return AIController(LLMService())


@router.post("/suggest", response_model=SuggestResponse)
async def suggest(
    data: SuggestRequest,
    controller: AIController = Depends(get_controller),
) -> SuggestResponse:
    return await controller.suggest(data)
