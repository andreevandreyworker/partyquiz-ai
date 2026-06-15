from pydantic import BaseModel, Field


class SuggestRequest(BaseModel):
    draft: str = Field(default="", max_length=512)
    language: str = Field(default="ru", pattern="^(ru|en)$")


class SuggestResponse(BaseModel):
    question: str
