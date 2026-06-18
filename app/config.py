from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ai_base_url: str
    ai_api_key: str = ""
    ai_model: str = "claude-sonnet-4"
    ai_timeout: float = 30.0
    config_db_url: str = ""
    redis_url: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"


settings = Settings()
