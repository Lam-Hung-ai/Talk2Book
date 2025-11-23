from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PgParts(BaseModel):
    host: str = "localhost"
    port: str = "5432"
    user: str = "postgres"
    password: SecretStr = SecretStr("pass")
    database: str = "talk2book"
    options: dict[str, str] = Field(default_factory=dict)

    def dsn(self) -> str:
        pwd = quote_plus(self.password.get_secret_value(), safe="")
        user = quote_plus(self.user)
        query = "&".join(f"{k}={v}" for k, v in self.options.items())

        return (
            f"postgresql+asyncpg://{user}:{pwd}@{self.host}:{self.port}/{self.database}"
            + (f"?{query}" if query else "")
        )


class Log(BaseModel):
    level: str = "INFO"
    output: str = "console"
    file_path: str = "default"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=Path(__file__).resolve().parents[2].joinpath(".env"),
        case_sensitive=False,
    )

    BACKEND_DIR: str = str(Path(__file__).resolve().parents[2])

    PROJECT_NAME: str = "Talk 2 Book"
    API_V1_STR: str = "api/v1"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    SECRET_KEY: str = "f528196732e95b603041ba3628b839196ee278f89941633206bf46d217d42621"
    JWT_ALG: str = "HS256"

    COOKIE_REFRESH_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"  # "lax", "strict", "none"
    COOKIE_DOMAIN: str | None = None
    COOKIE_PATH: str | None = None

    postgres: PgParts = PgParts()

    logging: Log = Log()

    @property
    def database_url(self) -> str:
        return self.postgres.dsn()


settings = Settings()
print("✅ Loaded .env from:", Path(__file__).resolve().parents[2].joinpath(".env"))
print("✅ Database URL:", settings.database_url)
print("✅ Backend directory:", settings.BACKEND_DIR)
