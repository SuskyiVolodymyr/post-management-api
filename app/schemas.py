from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    text: str
    auto_reply: bool = False
    auto_reply_time: int = 0


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    author_id: int
    date_time_created: datetime
    is_blocked: bool

    class Config:
        orm_mode = True
