from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import UserModel, Todo
import schemas


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "90bba2eecc6d3ad94ef1a3b741a528b6eae443373fbe30724e0357c4ea7b9767"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(plain_password: str):
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_id(db: Session, id: int):
    return db.query(UserModel).filter(UserModel.id == id).first()


def get_all_users(db: Session):
    return db.query(UserModel).filter().all()


def add_user(db: Session, user_data: schemas.UserCreateSchema):
    hashed_password = hash_password(user_data.password)
    db_user = UserModel(
        email=user_data.email,
        l_name=user_data.l_name,
        f_name=user_data.f_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid JWT",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credential_exception
        token_data = schemas.TokenDataSchema(email=email)
    except JWTError:
        raise credential_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credential_exception
    return user


def get_user_todos(
        db: Session,
        current_user: UserModel,
):
    todos = db.query(Todo).filter(Todo.owner == current_user).all()
    return todos


def add_todo(
        todo_data: schemas.TodoSchema,
        db: Session,
        current_user: UserModel,
):
    todo: Todo = Todo(
        title=todo_data.title,
    )
    todo.owner = current_user
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(
        db: Session,
        new_todo: schemas.TodoUpdateSchema,
):
    todo: Todo = db.query(Todo).filter(
        Todo.id == new_todo.id,
    ).first()
    todo.title = new_todo.title
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(
        db: Session,
        todo_id: int,
):
    todo: Todo = db.query(Todo).filter(Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
