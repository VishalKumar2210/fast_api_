import enum
from src.app.database.database import Base, engine
from sqlalchemy import Column, Integer, String, Boolean, Enum


def create_tables():
    Base.metadata.create_all(engine)


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"
    # all = admin, user


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)