from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr


# User Schema
class UserBase(BaseModel):
    email: EmailStr


class UserSchema(UserBase):
    id: int
    f_name: str
    l_name: str

    class Config:
        orm_mode = True


class UserCreateSchema(UserSchema):
    password: str

    class Config:
        orm_mode = True


# Token Schema
class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    email: Optional[str] = None


# Todos Schema
class TodoBaseSchema(BaseModel):
    title: str


class TodoSchema(TodoBaseSchema):
    user_id: int

    class Config:
        orm_mode = True


class TodoResponseSchema(TodoSchema):
    id: int


class TodoUpdateSchema(TodoBaseSchema):
    id: int

