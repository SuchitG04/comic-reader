from sqlmodel import Session, create_engine, SQLModel
from app.models import UserInfo
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL, echo=True)
SQLModel.metadata.create_all(engine)
