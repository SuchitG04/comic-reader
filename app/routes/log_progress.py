from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.routes.user import oauth2_scheme
from app.schemas import ReadingProgressPayload
from app.database import engine
from app.models import ReadingProgress

router = APIRouter(
    prefix="/log_progress",
    tags=["log_progress"],
    dependencies=[Depends(oauth2_scheme)]
)

@router.get("/user/{user_id}")
async def get_user_progress(user_id: int):
    with Session(engine) as session:
        stmt = select(ReadingProgress).where(ReadingProgress.user_id == user_id)
        readingprogress = session.exec(stmt).all()
        if len(readingprogress) == 0:
            return {"message": "No reading progress"}
        else:
            return {"readingprogress": readingprogress}


@router.put("/")
async def add_progress(progress_payload: ReadingProgressPayload):
    with (Session(engine) as session):
        is_present_stmt = (
            select(ReadingProgress)
            .where(ReadingProgress.user_id == progress_payload.user_id, ReadingProgress.bookrepo_id == progress_payload.book_id)
        )
        check_progress = session.exec(is_present_stmt).one_or_none()
        if not check_progress:
            new_progress = ReadingProgress(
                user_id=progress_payload.user_id,
                bookrepo_id=progress_payload.book_id,
                page_num=progress_payload.page_num
            )
        else:
            check_progress.page_num = progress_payload.page_num
            new_progress = check_progress

        try:
            session.add(new_progress)
        except Exception as e:
            session.rollback()
            print(e)
            raise HTTPException(
                detail="Database integrity compromised.",
                status_code=status.HTTP_409_CONFLICT
            )
        else:
            session.commit()
        session.refresh(new_progress)
        return new_progress
