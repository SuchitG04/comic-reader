from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from datetime import datetime

class UserInfo(SQLModel, table=True):
    __tablename__ = "userinfo"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    hash: str = Field(exclude=True)

    comment: list["Comment"] | None = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete"})
    readingprogress: list["ReadingProgress"] | None = Relationship(back_populates="userinfo", sa_relationship_kwargs={"cascade": "all, delete"})


class BookRepo(SQLModel, table=True):
    __tablename__ = "bookrepo"
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, unique=True)
    author_id: int = Field(sa_column=Column(Integer, ForeignKey("author.id", ondelete="CASCADE"), nullable=False))
    comicpdf_id: int = Field(sa_column=Column(Integer, ForeignKey("comicpdf.id", ondelete="CASCADE"), nullable=False))
    comicthumbnail_id: int = Field(sa_column=Column(Integer, ForeignKey("comicthumbnail.id", ondelete="CASCADE"), nullable=False))

    author: "Author" = Relationship(back_populates="bookrepo")
    comicpdf: "ComicPdf" = Relationship(back_populates="bookrepo")
    comicthumbnail: "ComicThumbnail" = Relationship(back_populates="bookrepo")
    comment: list["Comment"] | None = Relationship(back_populates="bookrepo", sa_relationship_kwargs={"cascade": "all, delete"})
    readingprogress: list["ReadingProgress"] | None = Relationship(back_populates="bookrepo", sa_relationship_kwargs={"cascade": "all, delete"})


class Author(SQLModel, table=True):
    __tablename__ = "author"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    bookrepo: list[BookRepo] = Relationship(back_populates="author", sa_relationship_kwargs={"cascade": "all, delete"})


class ComicPdf(SQLModel, table=True):
    __tablename__ = "comicpdf"
    id: int | None = Field(default=None, primary_key=True)
    file_path: str = Field(nullable=False, unique=True)

    bookrepo: BookRepo = Relationship(back_populates="comicpdf", sa_relationship_kwargs={"cascade": "all, delete"})


class ComicThumbnail(SQLModel, table=True):
    __tablename__ = "comicthumbnail"
    id: int | None = Field(default=None, primary_key=True)
    image_path: str = Field(nullable=False, unique=True)

    bookrepo: BookRepo = Relationship(back_populates="comicthumbnail", sa_relationship_kwargs={"cascade": "all, delete"})


class Comment(SQLModel, table=True):
    __tablename__ = "comment"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("userinfo.id", ondelete="CASCADE"), nullable=False))
    bookrepo_id: int = Field(sa_column=Column(Integer, ForeignKey("bookrepo.id", ondelete="CASCADE"), nullable=False))
    content: str = Field(nullable=False)
    timestamp: datetime = Field(nullable=False)

    userinfo: UserInfo = Relationship(back_populates="comment")
    bookrepo: BookRepo = Relationship(back_populates="comment")


class ReadingProgress(SQLModel, table=True):
    __tablename__ = "readingprogress"
    id: int | None = Field(default=None, primary_key=True)
    page_num: int = Field(nullable=False)
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("userinfo.id", ondelete="CASCADE"), nullable=False))
    bookrepo_id: int = Field(sa_column=Column(Integer, ForeignKey("bookrepo.id", ondelete="CASCADE"), nullable=False))

    userinfo: UserInfo = Relationship(back_populates="readingprogress")
    bookrepo: BookRepo = Relationship(back_populates="readingprogress")
