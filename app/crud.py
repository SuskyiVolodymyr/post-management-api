import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from AI.ai_tools import generate_comment_reply
from app import schemas
from db import models

load_dotenv()

PROFANITY_FILTER_API = "https://api.api-ninjas.com/v1/profanityfilter?text={}"


def get_all_posts(db: Session):
    return db.execute(select(models.Post)).scalars().all()


def create_post(db: Session, post: schemas.PostCreate, author_id: int):
    response = requests.get(
        PROFANITY_FILTER_API.format(f"{post.title} {post.text}"),
        headers={"X-Api-Key": os.getenv("API_NINJAS_KEY")},
    )
    is_blocked = False
    if response.status_code == 200:
        is_blocked = response.json()["has_profanity"]
    db_post = models.Post(
        author_id=author_id,
        title=post.title,
        text=post.text,
        auto_reply=post.auto_reply,
        auto_reply_time=post.auto_reply_time,
        is_blocked=is_blocked,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post_by_id(db: Session, post_id: int):
    return db.execute(select(models.Post).where(models.Post.id == post_id)).scalar()


def update_post(db: Session, post_id: int, post: schemas.PostCreate):
    db_post = get_post_by_id(db=db, post_id=post_id)
    db_post.text = post.text
    db_post.auto_reply = post.auto_reply
    db_post.auto_reply_time = post.auto_reply_time
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int):
    db_post = get_post_by_id(db=db, post_id=post_id)
    db.delete(db_post)
    db.commit()


def get_all_comments(db: Session, post_id: int | None = None):
    queryset = db.query(models.Comment)

    if post_id:
        queryset = queryset.filter(models.Comment.post_id == post_id)

    return queryset.all()


def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int):
    response = requests.get(
        PROFANITY_FILTER_API.format(comment.text),
        headers={"X-Api-Key": os.getenv("API_NINJAS_KEY")},
    )
    is_blocked = False
    if response.status_code == 200:
        is_blocked = response.json()["has_profanity"]

    db_comment = models.Comment(
        author_id=author_id,
        text=comment.text,
        post_id=comment.post_id,
        is_blocked=is_blocked
    )
    post = get_post_by_id(db=db, post_id=comment.post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    if post.auto_reply and not comment.is_blocked and not post.is_blocked:
        reply = models.Comment(
            author_id=post.author_id,
            text=generate_comment_reply(comment.text, post.text),
            post_id=post.id
        )
        db.add(reply)
        db.commit()

    return db_comment


def get_comment_by_id(db: Session, comment_id: int):
    return db.execute(select(models.Comment).where(models.Comment.id == comment_id)).scalar()


def update_comment(db: Session, comment_id: int, comment: schemas.CommentCreate):
    db_comment = get_comment_by_id(db=db, comment_id=comment_id)
    db_comment.text = comment.text
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int):
    db_comment = get_comment_by_id(db=db, comment_id=comment_id)
    db.delete(db_comment)
    db.commit()


def comments_analysis(db: Session, date_from: str, date_to: str):
    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")

    results = (
        db.query(
            func.date(models.Comment.date_time_created).label("day"),
            func.count(models.Comment.id).label("total_comments"),
            func.count(
                models.Comment.id
            ).filter(models.Comment.is_blocked == True).label("blocked_comments")
        )
        .filter(
            models.Comment.date_time_created.between(date_from_dt, date_to_dt)
        )
        .group_by(func.date(models.Comment.date_time_created))
        .order_by(func.date(models.Comment.date_time_created))
        .all()
    )

    analytics = [
        {
            "day": result.day,
            "total_comments": result.total_comments,
            "blocked_comments": result.blocked_comments
        }
        for result in results
    ]

    return analytics
