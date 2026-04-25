from dataclasses import dataclass

from backend.db.postgres_conn import PostgresConnection
from backend.db.redis_conn import RedisConnection


@dataclass # this decorator automatically generates boilerplate code for classes that mainly store data.
class DatabaseState:

    postgres : PostgresConnection
    redis : RedisConnection

    async def connect_all(self):
        """method to create all database connections"""
        await self.postgres.connect()
        await self.redis.connect()

    async def disconnect_all(self):
        """method to close all database connections"""
        await self.postgres.disconnect()
        await self.redis.disconnect()

    async def health_checks(self) -> dict[str, bool]:
        """method to check if all database connections are alive"""
        return {
            "postgres": await self.postgres.health_check(),
            "redis": await self.redis.health_check()
        }

def create_database_state(settings) -> DatabaseState:
    """Factory method for creating database state instance"""
    if settings is None:
        raise RuntimeError("Settings must be provided to create DatabaseState")

    postgres_conn = PostgresConnection(settings = settings)
    redis_conn = RedisConnection(settings = settings)

    return DatabaseState(
        postgres = postgres_conn,
        redis = redis_conn
    )

_global_db_state: DatabaseState | None = None

def set_global_db_state(db_state :DatabaseState):
    """Set global database state (called from main.py)."""
    global _global_db_state
    _global_db_state = db_state

def get_global_db_state()->DatabaseState:
    """Get global database state for agents."""
    if _global_db_state is None:
        raise RuntimeError("No global database state")
    return _global_db_state

