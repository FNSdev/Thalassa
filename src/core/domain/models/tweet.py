from datetime import datetime

from pydantic import BaseModel


class Tweet(BaseModel):
    id: int
    created_at: datetime | None
    saved_at: datetime
    text: str
    author_id: int | None
    conversation_id: int | None
    data: dict
