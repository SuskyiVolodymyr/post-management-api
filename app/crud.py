from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from db import models


def get_all_posts(db: Session):
    return db.execute(select(models.Post)).scalars().all()


def create_post(db: Session, post: schemas.PostCreate, author_id: int):
    db_post = models.Post(
        author_id=author_id,
        title=post.title,
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


def get_all_comments(db: Session, post_id: int | None = None):
    queryset = db.query(models.Comment)

    if post_id:
        queryset = queryset.filter(models.Comment.post_id == post_id)

    return queryset.all()


def create_comment(db: Session, comment: schemas.CommentCreate, author_id: int):
    db_comment = models.Comment(
        author_id=author_id,
        text=comment.text,
        post_id=comment.post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
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
