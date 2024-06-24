from fastapi import FastAPI
from sqlmodel import Session, SQLModel

from app.routes import user
from . import models
from app.database import engine

app = FastAPI()
app.include_router(user.router)

@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(engine)
