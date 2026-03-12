from fastapi import FastAPI, Request

from app.api.v1.router import router
from app.db.session import engine
from app.db.base import Base

from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from app.core.errors import validation_exception_handler, global_exception_handler

app = FastAPI()

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request: {request.method} {request.url.path} - Completed in {process_time:.4f}s")
    return response

app.include_router(router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)