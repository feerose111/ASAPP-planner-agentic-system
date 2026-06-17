import traceback
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from backend.core.config import settings
from backend.db.state import create_database_state
from backend.api import router as v1_router
from backend.core.exceptions import register_exception_handlers

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application Lifespan context manager"""
    db_state = create_database_state(settings = settings)

    try:
        logger.info(f"Starting database connection")
        await db_state.connect_all()
        logger.info(f"Database connection established")

        _app.state.db = db_state

        from backend.db.state import set_global_db_state
        set_global_db_state(db_state)
        logger.info(f"Application startup completed")
        yield

    except Exception as e:
        logger.info(f"Application startup failed with error: {e}")
        raise

    finally:
        await db_state.disconnect_all()
        logger.info(f"Database connection closed")

app = FastAPI(
    title="ASAPP - Planner Application",
    version="0.0.1",
    lifespan=lifespan,
)

register_exception_handlers(app)


@app.get("/healthcheck")
async def healthcheck():
    return {
        "status": "healthy"
    }

@app.get("/healthcheck/db")
async def healthcheck():
    """Detailed health check including database"""

    try:
        db_state = app.state.db
        db_health = await db_state.healthcheck()
        return {
            "status" : "healthy" if all(db_health.values()) else "unhealthy",
            "databases" : db_health
        }
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Health check failed with error: {e}")
        return { "status" : "unhealthy" , "databases": {} }


app.include_router(v1_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )