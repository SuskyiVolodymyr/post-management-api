from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from db.engine import SessionLocal

app = FastAPI()


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/posts/", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    return crud.get_all_posts(db=db)


@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post)
