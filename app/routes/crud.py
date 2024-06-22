from sqlmodel import Session, create_engine, SQLModel
from app.models import UserInfo
import os

DB_PASS = os.getenv("DB_PASS")
DB_URL = "postgresql://postgres:KissMySquid>.<@localhost/comic_reader"

engine = create_engine(DB_URL, echo=True)
SQLModel.metadata.create_all(engine)

def add_stuff():
    user1 = UserInfo(username="user1", hash="hash1", avatar="avatar1")

    with Session(engine) as session:
        session.add(user1)
        session.commit()

def main():
    add_stuff()

if __name__ == "__main__":
    main()
