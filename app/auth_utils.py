from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
)
from sqlmodel import Session, select
from starlette.responses import JSONResponse

from app.database import engine
from app.models import UserInfo
from app.schemas import Token, SignUp

import os
from dotenv import load_dotenv
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))

def verify_user(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def authenticate_user(username: str, password: str) -> UserInfo | bool:
    with Session(engine) as session:
        get_user_stmt = select(UserInfo).where(UserInfo.username == username)
        user = session.exec(get_user_stmt).one_or_none()

    # uncomment for testing to circumvent auth
    # hashed_password = hash_password(password)
    if not user:
        return False
    if not verify_user(password, user.hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

