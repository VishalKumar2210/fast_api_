from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.app.auth.models import UserRole
from src.app.auth import models


class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[models.UserRole] = UserRole.user  # Role should be either 'admin' or 'user'
    is_active: Optional[bool] = True


# Schema for showing user data
class UserResponse(BaseModel):
    id: int
    username: str
    role: models.UserRole
    # created_at: datetime
    # updated_at: datetime


class UserUpdate(BaseModel):
    is_active: bool
    role: models.UserRole


# Schema for login
class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
