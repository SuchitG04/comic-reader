from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class SignUp(BaseModel):
    username: str
    password: str
    confirm_password: str
