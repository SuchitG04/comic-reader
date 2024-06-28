from pydantic import BaseModel
from app.models import UserInfo

class SignUp(BaseModel):
    username: str
    password: str
    confirm_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo

