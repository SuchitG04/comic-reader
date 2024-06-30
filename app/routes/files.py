from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.database import engine
from app.models import BookRepo
from app.routes.user import oauth2_scheme

router = APIRouter(dependencies=[Depends(oauth2_scheme)])

@router.get(
    "/comic/{comic_title}",
)
async def get_comic(comic_title: str) -> FileResponse:
    with Session(engine) as session:
        get_book_stmt = select(BookRepo).where(BookRepo.title == comic_title)
        book = session.execute(get_book_stmt).one_or_none()
    if book is None:
        raise HTTPException(
            detail="Book not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    else:
        book = book[0]
    return FileResponse(path=book.file_path)
