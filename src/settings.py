import logging.config
import os

from pydantic import BaseSettings

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def setup_logging() -> None:
    logging.config.fileConfig(
        os.path.join(_ROOT_DIR, "logging.cfg"),
        disable_existing_loggers=False,
    )


class Settings(BaseSettings):
    TWITTER_API_KEY: str
    TWITTER_KEY_SECRET: str
    TWITTER_BEARER_TOKEN: str

    class Config:
        env_file = ".env.local"


settings = Settings()
