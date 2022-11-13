from abc import ABC, abstractmethod

from core.domain.models.twitter_user import TwitterUser


class TwitterUserRepository(ABC):
    @abstractmethod
    def create_or_update(self, id_: int, username: str, location: str | None) -> TwitterUser:
        raise NotImplementedError
