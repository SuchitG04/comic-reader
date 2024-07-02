from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.routes.user import oauth2_scheme
from app.database import engine
from app.models import Comment
from app.schemas import CommentPayload

router = APIRouter(
    prefix="/comments",
    dependencies=[Depends(oauth2_scheme)]
)

@router.get(
    "/",
    tags=["comments"]
)
async def get_comments():
    get_comments_stmt = select(Comment)
    with Session(engine) as session:
        comments = session.exec(get_comments_stmt).all()

    # handle this better
    if len(comments) == 0:
        return {"message": "No comments found"}
    else:
        return {"comments": comments}


@router.get(
    "/user/{user_id}",
    tags=["comments"]
)
async def get_user_comments(user_id: int):
    """Get all comments made by a user"""
    with Session(engine) as session:
        stmt = select(Comment).where(Comment.user_id == user_id)
        comments = session.exec(stmt).all()
    if len(comments) == 0:
        return {"message": "User has no comments"}
    else:
        return {"comments": comments}

@router.put(
    "/user/{user_id}",
    tags=["comments"]
)
async def create_comment(user_id: int, content: str) -> Comment:
    """Create a new comment from user_id and the comment text"""
    comment = Comment(user_id=user_id, content=content)
    try:
        with Session(engine) as session:
            session.add(comment)
            session.commit()
            # refresh to update the comment object with the key created by the db
            session.refresh(comment)
    except IntegrityError as e:
        print(e)
        raise HTTPException(
            detail="Database integrity compromised.",
            status_code=status.HTTP_409_CONFLICT
        )
    return comment
