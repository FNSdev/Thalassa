from datetime import datetime

from pydantic import BaseModel


class TwitterUser(BaseModel):
    id: int
    saved_at: datetime
    username: str
    location: str | None
