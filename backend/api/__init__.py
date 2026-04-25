from fastapi import APIRouter
from .v1.user import user_router
from .v1.auth import auth_router

router = APIRouter()

router.include_router(user_router)
router.include_router(auth_router)
