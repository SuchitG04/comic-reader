from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.routes.user import oauth2_scheme
from app.database import engine
from app.models import Comment

router = APIRouter(dependencies=[Depends(oauth2_scheme)])

@router.get("/comments/")
async def get_comments():
    get_comments_stmt = select(Comment)
    with Session(engine) as session:
        comments = session.exec(get_comments_stmt).all()

    if len(comments) == 0:
        return {"message": "No comments found"}
    else:
        return {"comments": comments}


@router.get("/comments/id/{comment_id}")
async def get_comment(comment_id: int) -> Comment:
    get_comment_stmt = select(Comment).where(Comment.id == comment_id);
    with Session(engine) as session:
        comment = session.exec(get_comment_stmt).one()
    if comment is None:
        raise HTTPException(
            detail="Comment not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return comment


@router.put("/comments/")
async def create_comment(comment: Comment):
    try:
        with Session(engine) as session:
            session.add(comment)
            session.commit()
            session.refresh(comment)
    except IntegrityError:
        raise HTTPException(
            detail="Database integrity compromised.",
            status_code=status.HTTP_409_CONFLICT
        )
    return comment
