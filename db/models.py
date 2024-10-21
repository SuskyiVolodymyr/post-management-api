from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from db.engine import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    date_time_created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    is_blocked = Column(Boolean, default=False)
    auto_reply = Column(Boolean, default=False)
    auto_reply_time = Column(Integer, default=0)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    date_time_created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    is_blocked = Column(Boolean, default=False)
    post_id = Column(Integer, ForeignKey("posts.id"))

    post = relationship(Post)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
