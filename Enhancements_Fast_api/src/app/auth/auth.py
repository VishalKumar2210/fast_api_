import os
from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.app.auth import models, schemas
from src.app.auth.models import User, UserRole
from src.app.database.database import get_db

# APIRouter Setup
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Constants
SECRET_KEY = os.getenv("SECRET_KEY", "Your_default_Secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing Configuration
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

db_dependency = Annotated[Session, Depends(get_db)]


# ------------------------------------------
# Utility Functions
# ------------------------------------------


# Password Hashing and Verification
def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    user = bcrypt_context.verify(plain_password, hashed_password)
    print("User Verified: ", user)
    return user


# Token Creation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------------------
# Database Interaction Functions
# ------------------------------------------


# Get User by username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# get user by id
def get_user_by_id(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Create a new user in the database
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username, hashed_password=hashed_password, role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# update user
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    updated_data = user.model_dump(exclude_unset=True)  # partial update
    for key, value in updated_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    # db.refresh(db_user)
    return db_user


# delete user
def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    db.delete(db_user)
    db.commit()
    # db.refresh(db_user)
    return db_user


# ------------------------------------------
# Authentication Logic
# ------------------------------------------


def authenticate_user(username: str, password: str, db: Session):
    # Retrieve the user from the database based on username
    user = db.query(User).filter_by(username=username).first()

    # Check if user exists and if password is correct
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Return the user if authenticated successfully
    return user


# Get Current User from Token
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


# Get the Role of the Current User
def get_current_user_role(current_user: User = Depends(get_current_user)):
    return UserRole(current_user.role)


# ------------------------------------------
# Role Checker using class-based decorator
# ------------------------------------------
class role_checker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: schemas.UserCreate = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted"
            )


# ------------------------------------------
# API Route Handlers
# ------------------------------------------


# Register a new user
@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user: schemas.UserCreate, db: db_dependency):
    # Check if username already exists
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    return create_user(db=db, user=user)


# User login and token generation
@router.post("/login", response_model=schemas.Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
#                                  db: Session = Depends(get_db)):\
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    print("Check :", user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print("access_token_expires check", access_token_expires)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    print(f"Token generated: {access_token}")

    return {"access_token": access_token, "token_type": "bearer", "role": user.role}


# ------------------------------------------
# Admin-only API Routes
# ------------------------------------------


@router.put(
    "/update_user/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(role_checker([UserRole.admin]))],
)
async def update_user_route(
    user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)
):
    return update_user(db, user_id, user)


# Delete an existing user (Admin only)
@router.delete(
    "/delete_user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker([UserRole.admin]))],
)
async def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return None
