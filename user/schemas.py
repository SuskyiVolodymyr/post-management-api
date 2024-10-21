from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    email: str | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True
