from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    python_env: str = "development"
    hostname: str = "localhost"
    api_token: list[str]