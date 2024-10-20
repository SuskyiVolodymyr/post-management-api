from sqlalchemy.orm import Session

import schemas
from db import models


def get_all_posts(db: Session):
    return db.query(models.Post).all()


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
