from fastapi import APIRouter
from .v1.user import router as user_router
from .v1.auth import router as auth_router

router = APIRouter()

router.include_router(user_router)
router.include_router(auth_router)
