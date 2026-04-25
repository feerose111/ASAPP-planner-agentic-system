from backend.core.config import Settings
from backend.db.base import DatabaseConnection , SessionProvider
from loguru import logger
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy import text
from contextlib import asynccontextmanager
from typing import AsyncIterator

class PostgresConnection(DatabaseConnection, SessionProvider):
    """ class to establish a connection to a Postgres database """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._engine : AsyncEngine | None = None
        self._session_maker : async_sessionmaker | None = None

    async def connect(self):
        """Establish database connection to postgres"""
        db_url = self._settings.DATABASE_URL
        self._engine = create_async_engine(db_url)
        self._session_maker = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )
        logger.info("Postgres engine created successfully")

    async def disconnect(self):
        """Disconnect database connection"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Postgres engine disconnected")


    async def health_check(self) -> bool:
        """Health check for postgres connection"""
        if not self._engine:
            return False

        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                return True

        except Exception as e:
            logger.error(f"Postgres engine failed with error: {e}")
            return False

    @asynccontextmanager  #helps to create async context manager using async with
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Get postgres session for each request"""
        if not self._session_maker:
            raise RuntimeError(
                "Database not initialized. PostgresSQL configuration may be missing."
            )
        async with self._session_maker() as session:
            yield session

    @property   #this lets user use a function as an attribute
    def session_maker(self):
        """Get postgres session for agents outside the request lifecycle"""
        if not self._session_maker:
            raise RuntimeError(
                "Database not initialized. PostgresSQL configuration may be missing."
            )
        return self._session_maker





