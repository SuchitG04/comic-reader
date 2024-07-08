from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.schemas import Token, SignUpPayload
from app.auth_utils import *

router = APIRouter(prefix="/auth")

@router.post(
    "/token",
    tags=["auth"],
    response_model=Token,
)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
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
    return Token(access_token=access_token, token_type="bearer", user=user)


@router.get(
    "/user",
    tags=["auth"],
)
async def get_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInfo:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise credentials_exception
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    with Session(engine) as session:
        stmt = select(UserInfo).where(UserInfo.username == username)
        user = session.exec(stmt).one_or_none()
    if user is None:
        raise credentials_exception
    return user


@router.put(
    "/sign_up",
    tags=["auth"],
    status_code=status.HTTP_200_OK,
)
async def sign_up(signup_payload: SignUpPayload) -> UserInfo:
    with Session(engine) as session:
        get_user_stmt = select(UserInfo).where(UserInfo.username == signup_payload.username)
        user = session.exec(get_user_stmt).one_or_none()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    user = UserInfo(username=signup_payload.username, email=signup_payload.email, hash=hash_password(signup_payload.password))
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user
