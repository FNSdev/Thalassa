from datetime import datetime
from zoneinfo import ZoneInfo

from pymongo import MongoClient

from core import settings
from core.domain.models.tweet import Tweet
from core.ports.persistence import TweetRepository


class MongoDBTweetRepository(TweetRepository):
    def __init__(
        self,
        client: MongoClient,
        db_name: str = settings.MONGODB_DB_NAME,
        collection_name: str = "tweets",
    ) -> None:
        self._client = client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def create(
        self,
        id_: int,
        category: str,
        created_at: datetime | None,
        text: str,
        author_id: int | None,
        data: dict,
    ) -> Tweet:
        tweet = {
            "_id": id_,
            "category": category,
            "created_at": created_at,
            "saved_at": datetime.utcnow().replace(tzinfo=ZoneInfo("UTC")),
            "text": text,
            "author_id": author_id,
            "data": data,
        }
        self._collection.insert_one(document=tweet)
        return Tweet(
            id=id_,
            category=category,
            created_at=created_at,
            saved_at=tweet["saved_at"],
            text=text,
            author_id=author_id,
            data=data,
        )
