from .base import Base
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = 'users'

    __repr_fields__ = ['id', 'username']

    id : Mapped[int]  = mapped_column(Integer, primary_key=True)
    username : Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    email : Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password : Mapped[str] = mapped_column(String(255), nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)






