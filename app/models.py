from sqlmodel import Field, SQLModel
from datetime import date

class UserInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    hash: str
    avatar: str | None = None


class BookRepo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    author: str = Field(nullable=False)
    publish_date: date | None = None
    file_path: str = Field(nullable=False)

