from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from db.engine import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    date_time_created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    is_blocked = Column(Boolean, default=False)
    auto_reply = Column(Boolean, default=False)
    auto_reply_time = Column(Integer, default=0)

    author = relationship("User", back_populates="posts")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String, nullable=False)
    date_time_created = Column(DateTime, default=datetime.utcnow(), nullable=False)
    is_blocked = Column(Boolean, default=False)
    post_id = Column(Integer, ForeignKey("posts.id"))

    post = relationship(Post)
    author = relationship("User", back_populates="comments")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
