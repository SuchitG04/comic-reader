from pydantic import BaseModel
from app.models import UserInfo, Comment

class SignUpPayload(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class CommentPayload(BaseModel):
    user_id: int
    book_id: int
    content: str

class ReadingProgressPayload(BaseModel):
    user_id: int
    book_id: int
    page_num: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo

class ComicsResponse(BaseModel):
    id: int
    title: str
    author: str

class CommentsResponse(BaseModel):
    comment: Comment
    username: str