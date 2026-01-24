from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "RegimeShift Sentinel"
    ENV: str = "development"
    SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8
    # NOTE: Keep as a string so .env can use either:
    # - "*"
    # - "http://localhost:5173,http://localhost:3000"
    # - "[\"http://localhost:5173\",\"http://localhost:3000\"]"
    # We parse it into a list via the `cors_allow_origins` property below.
    CORS_ALLOW_ORIGINS: str = "*"

    POSTGRES_DSN: str = "postgresql+asyncpg://rs_user:rs_pass@postgres:5432/rs_db"
    REDIS_URL: str = "redis://redis:6379/0"

    RATE_LIMIT_PER_MINUTE: int = 120

    class Config:
        env_file = ".env"

    @property
    def cors_allow_origins(self) -> List[str]:
        raw = (self.CORS_ALLOW_ORIGINS or "").strip()
        if not raw:
            return []
        if raw == "*":
            return ["*"]
        if raw.startswith("["):
            try:
                import json

                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(v).strip() for v in parsed if str(v).strip()]
            except Exception:
                pass
        return [part.strip() for part in raw.split(",") if part.strip()]

settings = Settings()
