from fastapi import FastAPI

from app.api.v1.router import router
from app.db.session import engine
from app.db.base import Base

app = FastAPI()

app.include_router(router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)