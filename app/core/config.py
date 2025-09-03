import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    ALGORITHM: str = "HS256"
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class TestingSettings(Settings):
    DB_NAME: str = 'test-online-library-backend'

    model_config = SettingsConfigDict(env_file=".env.test", extra="ignore")

def get_settings():
    if os.getenv("TESTING") == "1":
        return TestingSettings()
    return Settings()

settings = get_settings()