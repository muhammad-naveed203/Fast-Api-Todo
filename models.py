from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    f_name = Column(String)
    l_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserModel", back_populates="todos")
