from abc import ABC, abstractmethod
from datetime import datetime

from core.domain.models.tweet import Tweet


class TweetRepository(ABC):
    @abstractmethod
    def create(
        self,
        id_: int,
        created_at: datetime | None,
        text: str,
        author_id: int | None,
        conversation_id: int | None,
        data: dict,
    ) -> Tweet:
        pass
