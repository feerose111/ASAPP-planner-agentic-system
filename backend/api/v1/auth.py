from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.responses import APIResponse
from backend.core.cookies import set_refresh_cookie, clear_refresh_cookie
from backend.db.dependencies import (
    get_postgres_session,
    get_current_active_user,
    get_redis_client
)
from backend.schemas import SignUpRequest, LoginRequest
from backend.services.auth import register_user, login_user, logout_user, refresh_user_tokens

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
async def register(body: SignUpRequest, session: AsyncSession = Depends(get_postgres_session)):
    user, token = await register_user(session, body.email, body.password, body.username)
    return APIResponse(
        success=True,
        message="Signup successful",
        data={"token": token, "user": {"id": str(user.id), "email": user.email, "name": user.username}},
    )

@router.post("/signin")
async def login(
                response: Response,
                body : LoginRequest,
                session: AsyncSession = Depends(get_postgres_session)
):
    user, tokens = await login_user(session, body.email, body.password)
    set_refresh_cookie(response, tokens["refresh_token"])
    return APIResponse(
        success=True,
        message="Login successful",
        data={"token": tokens, "user": {"id": str(user.id), "email": user.email, "name": user.username}},
    )

@router.post("/refresh")
async def refresh(request: Request, response: Response, redis=Depends(get_redis_client)):
    tokens = await refresh_user_tokens(request, redis)
    set_refresh_cookie(response, tokens["refresh_token"])
    return APIResponse(
        success=True,
        message="Token Refreshed",
        data={"access_token": tokens["access_token"]}
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    redis = Depends(get_redis_client),
):
    await logout_user(request, redis)
    clear_refresh_cookie(response)
    return APIResponse(success=True, message="Logout successful")

@router.get("/me")
async def get_me(current_user = Depends(get_current_active_user)):
    return APIResponse(
        success=True,
        message="Current user",
        data={"id": str(current_user.id), "email": current_user.email, "name": current_user.name},
    )
