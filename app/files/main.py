from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.user import get_token

import os
from dotenv import load_dotenv
load_dotenv()
PDF_DIR = os.getenv("PDF_DIR")

files_app = FastAPI(dependencies=[Depends(get_token)])
files_app.mount("/static", StaticFiles(directory=PDF_DIR), name="static")
