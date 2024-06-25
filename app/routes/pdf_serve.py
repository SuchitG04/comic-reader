from fastapi import Depends, FastAPI
from app.routes.user import get_token

file_serve = FastAPI(dependencies=[Depends(get_token)])