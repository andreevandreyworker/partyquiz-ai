from app.dto import SuggestRequest, SuggestResponse
from app.services import LLMService


class AIController:
    def __init__(self, service: LLMService):
        self._service = service

    async def suggest(self, data: SuggestRequest) -> SuggestResponse:
        question = await self._service.suggest_question(
            data.draft, data.language
        )
        return SuggestResponse(question=question)
