import shutil
import os
from sqlmodel import Session, select
from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from pydantic import BaseModel

from app.routes.user import oauth2_scheme
from app.database import engine
from app.models import (
    BookRepo,
    Author,
    ComicPdf,
    ComicThumbnail
)

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(oauth2_scheme)]
)

def rename_file(filename: str, file_dir: str) -> str:
    i = 1
    filename_split = filename.split(".")
    while filename in os.listdir(f"app/files/{file_dir}"):
        filename_split[0] += f"_{i}"
        filename = filename_split[0] + "." + filename_split[1]
        i += 1
    return filename


@router.put("/books")
async def insert_book(
        file: Annotated[UploadFile, File()],
        thumb: Annotated[UploadFile, File()],
        title: Annotated[str, Form()],
        author_name: Annotated[str, Form()]
):
    if file.filename in os.listdir("app/files/books"):
        file.filename = rename_file(file.filename, "books")
    if thumb.filename in os.listdir("app/files/thumbnails"):
        thumb.filename = rename_file(thumb.filename, "thumbnails")
    with Session(engine) as session:
        author_check = session.exec(select(Author).where(Author.name == author_name)).one_or_none()
        if author_check is None:
            author = Author(name=author_name)
        else:
            author = author_check

        try:
            comicpdf = ComicPdf(file_path=f"app/files/books/{file.filename}")
            comicthumb = ComicThumbnail(image_path=f"app/files/thumbnails/{thumb.filename}")
            session.add(
                BookRepo(title=title, author=author, comicpdf=comicpdf, comicthumbnail=comicthumb)
            )
        except Exception as e:
            session.rollback()
            raise e
        else:
            session.commit()
    with open(f"app/files/books/{file.filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)
    with open(f"app/files/thumbnails/{thumb.filename}", "wb") as f:
        shutil.copyfileobj(thumb.file, f)
    return {"message": "done"}


@router.get("/books")
async def get_all_books():
    with Session(engine) as session:
        books = session.exec(select(BookRepo.title)).all()
    if books is not None:
        return {"books": books}
    return {"message": "Books not found"}


@router.delete("/books")
async def delete_book(title: str):
    with Session(engine) as session:
        stmt = select(BookRepo).where(BookRepo.title == title)
        book = session.exec(stmt).one_or_none()
        if book is None:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        session.delete(book)
        session.commit()
    return {"message": "Book deleted"}
