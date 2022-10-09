from functools import lru_cache

from pydantic import BaseSettings

class Settings(BaseSettings):
    mysql_host: str
    mysql_port: int
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()