from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.database import engine
from app.models import Base
from app.routers import auth, resume

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Analyzer")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(resume.router)
