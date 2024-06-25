from fastapi import FastAPI
from sqlmodel import SQLModel

from app.routes import user
from app.database import engine
from app.files.main import files_app

app = FastAPI()
app.include_router(user.router)
app.mount("/files/", files_app)

@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(engine)
