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

@router.put("/book")
async def insert_book(
        file: Annotated[UploadFile, File()],
        thumb: Annotated[UploadFile, File()],
        title: Annotated[str, Form()],
        author_name: Annotated[str, Form()]
):
    if file.filename in os.listdir("app/files/books") \
    or thumb.filename in os.listdir("app/files/thumbnails"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already present"
        )
    with Session(engine) as session:
        author_check = session.exec(select(Author).where(Author.name == author_name)).one_or_none()
        if author_check is None:
            author = Author(name=author_name)
            session.add(author)
        else:
            author = author_check

        try:
            comicpdf = ComicPdf(file_path=f"app/files/books/{file.filename}")
            comicthumb = ComicThumbnail(image_path=f"app/files/thumbnails/{thumb.filename}")
            session.add(comicpdf)
            session.add(comicthumb)
            session.commit()
            session.add(BookRepo(title=title, author_id=author.id, comicpdf_id=comicpdf.id, comicthumbnail_id=comicthumb.id))
        except:
            session.rollback()
            raise
        else:
            session.commit()
    with open(f"app/files/books/{file.filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)
    with open(f"app/files/thumbnails/{thumb.filename}", "wb") as f:
        shutil.copyfileobj(thumb.file, f)
    return {"message": "done"}

