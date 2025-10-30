from pathlib import Path
from urllib.parse import quote_plus, quote

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

        return f"postgresql+asyncpg://{user}:{pwd}@{self.host}:{self.port}/{self.database}" + (f"?{query}" if query else "")
        
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix = "APP_",
        env_nested_delimiter = "__",
        env_file = Path(__file__).resolve().parent.parent.joinpath(".env")
    )
    
    PROJECT_NAME: str = "Talk 2 Book"
    API_V1_STR: str = "api/v1"

    postgres: PgParts = PgParts()

    @property
    def database_url(self) -> str:
        return self.postgres.dsn()
    
settings = Settings()
print(settings.database_url)