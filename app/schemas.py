from pydantic import BaseModel
from app.models import UserInfo, Comment

class SignUpPayload(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class CommentPayload(BaseModel):
    content: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo

class ComicsResponse(BaseModel):
    id: int
    title: str
    author: str

class CommentsResponse(Comment):
    username: str