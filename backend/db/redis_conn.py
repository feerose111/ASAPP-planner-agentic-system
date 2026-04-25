from backend.core.config import Settings
from backend.db.base import DatabaseConnection
from loguru import logger
from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager
from typing import AsyncIterator

class RedisConnection(DatabaseConnection):

    def __init__(self, settings: Settings):
        self._settings = settings
        self._pool:  ConnectionPool | None = None

    async def connect(self):
        """Initiate Connection to Redis."""
        self._pool = ConnectionPool.from_url(
                        self._settings.REDIS_URL,
                        max_connections= 20,
                        decode_responses= True,
                    )
        logger.info(f"Redis connection pool initialized successfully.")

    async def disconnect(self):
        """close connection from Redis."""
        if self._pool:
            await self._pool.disconnect()
            logger.info(f"Redis connection closed successfully.")

    async def health_check(self) -> bool:
        """Check if Redis is active or not."""
        if not self._pool:
            return False

        try:
            async with Redis(connection_pool=self._pool) as client:
                await client.ping()
                return True

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[Redis]:
        """ Get client from connection pool."""
        if not self._pool:
            raise RuntimeError(f"Redis connection pool not initialized.")

        async with Redis(connection_pool=self._pool) as client:
            yield client
    
    @property
    def pool(self) -> ConnectionPool:
        if not self._pool:
            raise RuntimeError("Redis connection pool not initialized.")
        return self._pool


