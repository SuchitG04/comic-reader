from sqlmodel import Field, SQLModel

class UserInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    hash: str
    avatar: str | None = None

class BookRepo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    author_id: int = Field(nullable=False, foreign_key="author.id")
    comicpdf_id: int = Field(nullable=False, foreign_key="comicpdf.id")
    comicthumbnail_id: int = Field(foreign_key="comicthumbnail.id")

class Author(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

class ComicPdf(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_path: str = Field(nullable=False, unique=True)

class ComicThumbnail(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image_path: str = Field(nullable=False)

class Comment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, foreign_key="userinfo.id")
    content: str = Field(nullable=False)
