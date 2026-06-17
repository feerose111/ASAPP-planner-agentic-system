from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import AsyncGenerator

from backend.db.state import DatabaseState
from backend.core.exceptions import UnauthorizedException
from backend.core.auth import verify_token
from backend.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

def get_db_state(request: Request):
    """Returns object from app.state"""
    return request.app.state.db

async def get_postgres_session(
        db_state : DatabaseState = Depends(get_db_state),
) -> AsyncGenerator[AsyncSession]:
    """Returns postgres session"""
    async with db_state.postgres.get_session() as session:
        yield session

async def get_redis_client(
        db_state : DatabaseState = Depends(get_db_state),
) -> AsyncGenerator[Redis, None]:
    """Returns redis client"""
    async with db_state.redis.get_client() as client:
        yield client

#Get Current User Dependency

async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_postgres_session),
) -> User:

    if not credentials:
        raise UnauthorizedException("Authentication required")

    payload = verify_token(credentials.credentials, expected_type="access")

    user_id: str = payload.get("sub", {}).get("user_id")
    if not user_id:
        raise UnauthorizedException("Malformed token payload")

    user: User | None = await db.get(User, int(user_id))
    if not user:
        raise UnauthorizedException("User no longer exists")

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:

    if not current_user.is_active:
        raise UnauthorizedException("Account is disabled")

    return current_user





