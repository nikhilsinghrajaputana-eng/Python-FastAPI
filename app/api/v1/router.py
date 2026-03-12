from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, files

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(user.router, prefix="/users", tags=["Users"])
router.include_router(files.router, prefix="/files", tags=["Files"])