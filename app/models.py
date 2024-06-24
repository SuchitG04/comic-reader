from sqlmodel import Field, Relationship, SQLModel

class UserInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    username: str = Field(nullable=False, unique=True)
    hash: str
    avatar: str | None = None
