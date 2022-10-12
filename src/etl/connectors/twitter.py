import logging
from typing import Any

from tweepy import StreamingClient, Tweet

from src import settings, setup_logging

logger = logging.getLogger(__name__)


class TwitterConnector(StreamingClient):
    def __init(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def on_tweet(self, tweet: Tweet) -> None:
        logger.info("%s, %s, %s", tweet.id, tweet.author_id, tweet.conversation_id)


if __name__ == "__main__":
    setup_logging()

    connector = TwitterConnector(
        bearer_token=settings.TWITTER_BEARER_TOKEN,
        wait_on_rate_limit=True,
    )

    try:
        connector.sample()
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        connector.disconnect()
