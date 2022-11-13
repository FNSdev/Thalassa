import logging
from typing import Any

from tweepy import StreamingClient, StreamRule, Tweet

from core import settings, setup_logging
from core.adapters.persistence.mongodb.repositories import (
    MongoDBTweetRepository,
    MongoDBTwitterUserRepository,
)
from core.infrastructure.mongodb import client
from core.ports.persistence import TweetRepository, TwitterUserRepository

logger = logging.getLogger(__name__)


class TwitterConnector(StreamingClient):
    def __init__(
        self,
        tweet_repository: TweetRepository,
        twitter_user_repository: TwitterUserRepository,
        category: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self._tweet_repository = tweet_repository
        self._twitter_user_repository = twitter_user_repository
        self._category = category

    def on_tweet(self, tweet: Tweet) -> None:
        logger.info("Saving new tweet, id %s, author_id %s", tweet.id, tweet.author_id)
        self._tweet_repository.create(
            id_=tweet.id,
            category=self._category,
            created_at=tweet.created_at,
            text=tweet.text,
            author_id=tweet.author_id,
            data=tweet.data,
        )

    def on_includes(self, includes: dict) -> None:
        for user in includes.get("users", []):
            logger.info("Saving new twitter user, id %s", user.id)
            self._twitter_user_repository.create_or_update(
                id_=user.id,
                username=user.username,
                location=user.location,
            )


if __name__ == "__main__":
    setup_logging()

    connector = TwitterConnector(
        tweet_repository=MongoDBTweetRepository(client=client, collection_name="tweets_2"),
        twitter_user_repository=MongoDBTwitterUserRepository(client=client),
        category="covid",
        bearer_token=settings.TWITTER_BEARER_TOKEN,
        wait_on_rate_limit=True,
    )
    connector.add_rules(
        add=[StreamRule(value="(covid OR covid19) lang:en -is:retweet -is:reply", tag="covid")],
    )

    try:
        connector.filter(
            tweet_fields=["id", "created_at", "text", "author_id"],
            user_fields=["location"],
            expansions=["author_id"],
        )
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        connector.disconnect()
