from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 120
    database_url: str = f"sqlite:///{(BASE_DIR / 'pocketsmart.db').as_posix()}"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    use_ai: bool = True
    allowed_origins: list[str] = ["http://127.0.0.1:8000", "http://localhost:8000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def ai_enabled(self) -> bool:
        return self.use_ai and bool(self.gemini_api_key)

settings = Settings()
