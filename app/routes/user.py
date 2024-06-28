# move dependencies to dependencies.py

from datetime import datetime, timezone, timedelta
from typing import Annotated

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

router = APIRouter()


def verify_user(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def authenticate_user(username: str, password: str) -> UserInfo | bool:
    with Session(engine) as session:
        get_user_stmt = select(UserInfo).where(UserInfo.username == username)
        user = session.execute(get_user_stmt).one_or_none()

    if user is not None:
        user = user[0]
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


# payload should be email and password
@router.post(
    "/token",
    tags=["auth"],
    response_model=Token,
)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        {"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="token",
        value=access_token,
        expires=datetime.now(timezone.utc) + access_token_expires,
        samesite=None,
        domain="lostip.ddns.net",
    )
    return Token(access_token=access_token, token_type="bearer")


async def get_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    with Session(engine) as session:
        get_user_stmt = select(UserInfo).where(UserInfo.username == username)
        user = session.execute(get_user_stmt).one_or_none()
    if user is None:
        raise credentials_exception
    return user[0]


@router.get(
    "/user",
    tags=["auth"],
)
async def wrap_get_user(request: Request) -> UserInfo:
    if request.cookies.get("token") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return await get_user(request.cookies.get("token"))


@router.post(
    "/sign_up",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
async def sign_up(signup_payload: SignUp):
    with Session(engine) as session:
        get_user_stmt = select(UserInfo).where(UserInfo.username == signup_payload.username)
        user = session.execute(get_user_stmt).one_or_none()

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    user = UserInfo(username=signup_payload.username, hash=hash_password(signup_payload.password))
    with Session(engine) as session:
        session.add(user)
        session.commit()

