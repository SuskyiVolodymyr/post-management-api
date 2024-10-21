from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from db import models


def get_all_posts(db: Session):
    return db.execute(select(models.Post)).scalars().all()


def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(
        text=post.text,
        auto_reply=post.auto_reply,
        auto_reply_time=post.auto_reply_time,
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
