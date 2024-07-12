from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.routes import user
from app.database import engine
from app.routes import files
from app.routes import comments
from app.routes import log_progress
from app.internal import admin

app = FastAPI()
app.include_router(user.router)
app.include_router(files.router)
app.include_router(comments.router)
app.include_router(admin.router)
app.include_router(log_progress.router)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(engine)
