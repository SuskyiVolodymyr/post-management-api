from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session

from db.engine import SessionLocal

from app import crud as app_crud, schemas as app_schemas

app = FastAPI()


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/posts/", response_model=list[app_schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    return app_crud.get_all_posts(db=db)


@app.post("/posts/", response_model=app_schemas.Post)
def create_post(post: app_schemas.PostCreate, db: Session = Depends(get_db)):
    return app_crud.create_post(db=db, post=post)


@app.put("/posts/{post_id}", response_model=app_schemas.Post)
def update_post(post_id: int, post: app_schemas.PostCreate, db: Session = Depends(get_db)):
    return app_crud.update_post(db=db, post_id=post_id, post=post)


@app.get("/posts/{post_id}", response_model=app_schemas.Post)
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    return app_crud.get_post_by_id(db=db, post_id=post_id)


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    return app_crud.delete_post(db=db, post_id=post_id)
