from datetime import datetime
from zoneinfo import ZoneInfo

from pymongo import MongoClient

from core import settings
from core.domain.models.twitter_user import TwitterUser
from core.ports.persistence import TwitterUserRepository


class MongoDBTwitterUserRepository(TwitterUserRepository):
    def __init__(
        self,
        client: MongoClient,
        db_name: str = settings.MONGODB_DB_NAME,
        collection_name: str = "twitter_users",
    ) -> None:
        self._client = client
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]

    def create_or_update(self, id_: int, username: str, location: str | None) -> TwitterUser:
        now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        twitter_user = {"_id": id_, "username": username, "location": location}
        self._collection.update_one(
            filter={"_id": id_},
            update={"$setOnInsert": {"saved_at": now}, "$set": twitter_user},
            upsert=True,
        )
        return TwitterUser(id=id_, saved_at=now, username=username, location=location)
