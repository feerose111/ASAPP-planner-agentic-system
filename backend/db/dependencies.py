from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from backend.db.state import DatabaseState


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
):
    """Returns redis client"""
    async with db_state.redis.get_client() as client:
        yield client






