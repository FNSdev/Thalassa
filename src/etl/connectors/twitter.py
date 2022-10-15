import logging
from typing import Any

from tweepy import StreamingClient, Tweet

from core import settings, setup_logging
from core.adapters.persistence.mongodb.repositories import MongoDBTweetRepository
from core.infrastructure.mongodb import client
from core.ports.persistence import TweetRepository

logger = logging.getLogger(__name__)


class TwitterConnector(StreamingClient):
    def __init__(self, tweet_repository: TweetRepository, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._tweet_repository = tweet_repository

    def on_tweet(self, tweet: Tweet) -> None:
        logger.info("%s, %s, %s", tweet.id, tweet.author_id, tweet.conversation_id)
        self._tweet_repository.create(
            id_=tweet.id,
            created_at=tweet.created_at,
            text=tweet.text,
            author_id=tweet.author_id,
            conversation_id=tweet.conversation_id,
            data=tweet.data,
        )


if __name__ == "__main__":
    setup_logging()

    connector = TwitterConnector(
        tweet_repository=MongoDBTweetRepository(client=client, collection_name="tweets_0"),
        bearer_token=settings.TWITTER_BEARER_TOKEN,
        wait_on_rate_limit=True,
    )

    try:
        connector.sample()
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        connector.disconnect()
