from datetime import datetime
from fastapi import Request
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User
from backend.core.exceptions import (
    CustomException,
    UnauthorizedException,
)
from backend.core.auth import (
    hash_password,
    create_tokens,
    verify_password ,
    verify_token
)

async def register_user(session: AsyncSession, email: EmailStr, password: str, username: str):
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise CustomException(status_code=409, message="User already exists")

    user = User(email=email, password=hash_password(password), username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access_token, refresh_token = create_tokens({"user_id": str(user.id), "email": user.email})
    return user, {"access_token": access_token, "refresh_token": refresh_token}


async def login_user(session: AsyncSession, email: str, password: str) -> tuple[User, dict]:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Run hash comparison regardless so response time is constant
    password_correct = verify_password(password, user.password if user else "")

    if not user or not password_correct:
        raise UnauthorizedException(message="Invalid email or password")

    if not user.is_active:
        # 403, not 401 — the credentials are valid, the account is just banned
        raise CustomException(status_code=403, message="Account is disabled")

    access_token, refresh_token = create_tokens(
        {"user_id": str(user.id), "email": user.email}
    )
    return user, {"access_token": access_token, "refresh_token": refresh_token}

async def refresh_user_tokens(request: Request, redis) -> dict:
    raw = request.cookies.get("refresh_token")
    if not raw:
        raise UnauthorizedException("No refresh token provided")

    payload = verify_token(raw, expected_type="refresh")

    if await redis.get(f"blacklist:{payload['jti']}"):
        raise UnauthorizedException("Token has been revoked")

    ttl = payload["exp"] - int(datetime.utcnow().timestamp())
    if ttl > 0:
        await redis.setex(f"blacklist:{payload['jti']}", ttl, "1")

    access_token, refresh_token = create_tokens(
        {"user_id": payload["sub"]["user_id"], "email": payload["sub"].get("email", "")}
    )
    return {"access_token": access_token, "refresh_token": refresh_token}

async def logout_user(request: Request, redis) -> None:
    raw = request.cookies.get("refresh_token")
    if not raw:
        return

    try:
        payload = verify_token(raw, expected_type="refresh")
        ttl = payload["exp"] - int(datetime.utcnow().timestamp())
        if ttl > 0:
            await redis.setex(f"blacklist:{payload['jti']}", ttl, "1")
    except UnauthorizedException:
        pass


