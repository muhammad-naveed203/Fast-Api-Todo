from typing import Optional, List
from fastapi import FastAPI
from fastapi.params import Depends
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

import schemas
from datetime import timedelta, datetime
from fastapi import HTTPException
from database import get_db, Base, engine
from functions import add_user, verify_password, get_user_by_email, get_all_users, get_user_by_id, \
    ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, get_current_user, get_user_todos, update_todo, delete_todo, \
    add_todo
from models import UserModel


Base.metadata.create_all(engine)

app = FastAPI()


def authenticate_user(db: Session, email: str, password: str):
    user: UserModel = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.utcnow() + expires_delta
    else:
        expires = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get("/users", response_model=list[schemas.CreateUser])
def users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return list(users)


@app.post("/signup", response_model=schemas.CreateUser)
def sign_up(user_data: schemas.UserCreateSchema, db: Session = Depends(get_db)):
    user = get_user_by_email(db, user_data.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="email exist",
        )
    new_user = add_user(db, user_data)
    return new_user


@app.post("/token", response_model=schemas.TokenSchema)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user_data = authenticate_user(db, form_data.username, form_data.password)
    if not user_data:
        raise HTTPException(
            HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_expires_date = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user_data.email},
        expires_delta=token_expires_date,
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get("/user/{id:int}", response_model=schemas.CreateUser)
def get_user(id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail='user Not Found')


@app.post('/create_todo', response_model=List[schemas.TodoResponseSchema])
def add_todo_views(
        todo_data: schemas.TodoBaseSchema, db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    add_todo(todo_data, db, current_user)
    todos = get_user_todos(db, current_user)
    return todos


@app.get('/get_all_todos', response_model=List[schemas.TodoResponseSchema])
def get_my_todos(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    todos = get_user_todos(db, current_user)
    return todos


@app.put('/update', response_model=List[schemas.TodoResponseSchema])
def update_todo_view(
        todo_data: schemas.TodoUpdateSchema,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user),
):
    update_todo(
        db,
        new_todo=todo_data,
    )
    todos = get_user_todos(db, current_user)
    return todos


@app.delete('/{todo_id:int}', response_model=List[schemas.TodoResponseSchema])
def delete_todo_view(
        todo_id: int,
        db: Session = Depends(get_db),
        current_user: UserModel = Depends(get_current_user)
):
    delete_todo(db, todo_id)
    todos = get_user_todos(db, current_user)
    return todos