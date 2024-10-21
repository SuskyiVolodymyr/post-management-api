from datetime import timedelta

from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.engine import SessionLocal

from app import crud as app_crud, schemas as app_schemas
from user import crud as user_crud, schemas as user_schemas, auth

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.post("/register/", response_model=user_schemas.UserResponse)
def register(new_user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=new_user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return user_crud.create_user(db=db, user=new_user)


@app.post("/token/", response_model=user_schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, email=form_data.username)

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


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
