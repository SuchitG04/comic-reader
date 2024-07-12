from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, distinct
from pydantic import AfterValidator

from app.routes.user import oauth2_scheme
from app.database import engine
from app.models import Comment, UserInfo
from app.schemas import CommentPayload, CommentsResponse

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(oauth2_scheme)]
)

@router.get("/book/{book_id}")
async def get_comments(book_id: int) -> dict[str, str] | dict[str, list[CommentsResponse]]:
    """Get all comments for a book"""
    def get_username_retrieving_stmt(user_id):
        """Returns a statement selecting the username corresponding to the given user_id"""
        get_usernames_stmt = (
            select(distinct(UserInfo.username))
            .join(Comment, Comment.user_id == UserInfo.id)
            .where(Comment.bookrepo_id == book_id)
            .where(Comment.user_id == user_id)
        )
        return get_usernames_stmt

    with Session(engine) as session:
        get_comments_stmt = select(Comment).where(Comment.bookrepo_id == book_id)
        comments = session.exec(get_comments_stmt).all()
        comments_out = []
        # gets and adds the username to the response model.
        # does this by first retrieving username given the user_id in each of the comments instance and of course the
        # book_id in the path params
        for comment in comments:
            stmt = get_username_retrieving_stmt(comment.user_id)
            username = session.exec(stmt).one()
            comments_out.append(CommentsResponse(comment=comment, username=username))

        if len(comments) == 0:
            return {"message": "No comments found"}
        else:
            return {"comments": comments_out}


@router.get("/user/{user_id}")
async def get_user_comments(user_id: int):
    """Get all comments made by a user"""
    with Session(engine) as session:
        stmt = select(Comment).where(Comment.user_id == user_id)
        comments = session.exec(stmt).all()
    if len(comments) == 0:
        return {"message": "User has no comments"}
    else:
        return {"comments": comments}

@router.put("/")
async def create_comment(payload: CommentPayload,) -> CommentsResponse:
    """Create a new comment from user_id and the comment text"""
    comment = Comment(user_id=payload.user_id, bookrepo_id=payload.book_id, content=payload.content, timestamp=datetime.now())
    with Session(engine) as session:
        try:
            username = session.exec(
                select(UserInfo.username).where(UserInfo.id == payload.user_id)
            ).one()
            session.add(comment)
        except Exception as e:
            session.rollback()
            print(e)
            raise HTTPException(
                detail="Database integrity compromised.",
                status_code=status.HTTP_409_CONFLICT
            )
        else:
            session.commit()
        # refresh to update the comment object with the key created by the db
        session.refresh(comment)
    comment_out = CommentsResponse(comment=comment, username=username)
    return comment_out
