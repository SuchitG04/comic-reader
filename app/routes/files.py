from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.database import engine
from app.models import BookRepo, Author, ComicThumbnail, ComicPdf
from app.routes.user import oauth2_scheme
from app.schemas import ComicsResponse

router = APIRouter(dependencies=[Depends(oauth2_scheme)])

@router.get(
    "/comics/",
    tags=["comics"],
    response_model=list[ComicsResponse]
)
async def get_all_comics():
    with Session(engine) as session:
        stmt = (
            select(BookRepo.id, BookRepo.title, ComicThumbnail.image_path, Author.name)
            .join(ComicThumbnail, BookRepo.comicthumbnail_id == ComicThumbnail.id)
            .join(Author, BookRepo.author_id == Author.id)
        )
        res = session.exec(stmt).all()
    comic_list = []
    for book in res:
        comic_list.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.name,
            }
        )
    return comic_list


@router.get(
    "/comics/id/{comic_id}",
    tags=["comics"]
)
async def get_comic(comic_id: int) -> FileResponse:
    with Session(engine) as session:
        stmt = (
            select(ComicPdf.file_path)
            .join(BookRepo, ComicPdf.id == BookRepo.comicpdf_id)
            .where(ComicPdf.id == comic_id)
        )
        book: str = session.exec(stmt).one_or_none()
    if book is None:
        raise HTTPException(
            detail="Book not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return FileResponse(path=book)


@router.get(
    "/comics/thumbnail/{comic_id}",
    tags=["comics"]
)
async def get_comic_thumbnail(comic_id: int) -> FileResponse:
    return FileResponse(path=f"app/files/thumbnails/{comic_id}.jpg")
