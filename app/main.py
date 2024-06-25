from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel

from app.routes import user
from . import models
from app.database import engine
from app.routes.pdf_serve import file_serve

app = FastAPI()
app.include_router(user.router)
app.mount("/file_serve", file_serve)
file_serve.mount("/static", StaticFiles(directory="./books"), name="static")

@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(engine)
