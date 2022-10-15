import logging.config
import os

from pydantic import BaseSettings

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_logging() -> None:
    logging.config.fileConfig(
        os.path.join(_ROOT_DIR, "logging.cfg"),
        disable_existing_loggers=False,
    )


class Settings(BaseSettings):
    MONGODB_HOST: str
    MONGODB_PORT: int = 27017
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_DB_NAME = "thalassa"

    TWITTER_API_KEY: str
    TWITTER_KEY_SECRET: str
    TWITTER_BEARER_TOKEN: str

    class Config:
        env_file = ".env.local"


settings = Settings()
