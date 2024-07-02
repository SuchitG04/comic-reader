from pydantic import BaseModel
from app.models import UserInfo

class SignUpPayload(BaseModel):
    username: str
    password: str
    confirm_password: str

class CommentPayload(BaseModel):
    user_id: int
    content: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo

class ComicsResponse(BaseModel):
    id: int
    title: str
    author: str
