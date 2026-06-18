from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, code: str | None = None):
        self.code = code or self.__class__.code
        super().__init__(self.code)


class AIUnavailableError(AppError):
    status_code = 502
    code = "ai_unavailable"


class RateLimitError(AppError):
    status_code = 429
    code = "ai_rate_limited"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(
        request: Request, exc: AppError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code},
        )
