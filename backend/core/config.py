from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL : str
    POSTGRES_USER : str = "asapp"
    POSTGRES_PASSWORD : str
    POSTGRES_PORT : int = 5432
    POSTGRES_DB : str  = "asapp_db"

    SECRET_KEY: str
    OPENROUTER_API_KEY : str
    DEBUG: bool = True


    REDIS_URL: str | None = None
    QDRANT_URL: str | None = None


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()



