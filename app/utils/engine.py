"""The utils engine module."""

import logging
from fastapi import (
    FastAPI,
)
from motor.motor_asyncio import (
    AsyncIOMotorClient,
)
from odmantic import (
    AIOEngine,
)

from app.config import (
    settings,
)

logger = logging.getLogger(__name__)

async def init_engine_app(app: FastAPI) -> None:
    """
    Creates database and connections to the database.

    This function creates a mongodb client instance,
    and an odmantic engine and stores them in the
    application's state property.

    Args:
        app (fastapi.FastAPI): fastAPI application.
    """
    app_settings = settings()

    logger.info(f"MONGODB_USERNAME: {app_settings.MONGODB_USERNAME}")
    logger.info(f"MONGODB_HOST: {app_settings.MONGODB_HOST}")
    logger.info(f"MONGODB_DATABASE: {app_settings.MONGODB_DATABASE}")

    # Формируем URL для MongoDB
    host = app_settings.MONGODB_HOST.replace("mongodb+srv://", "")
    mongodb_url = f"mongodb+srv://{app_settings.MONGODB_USERNAME}:{app_settings.MONGODB_PASSWORD}@{host}/?retryWrites=true&w=majority"

    logger.info(f"MongoDB URL: {mongodb_url}")

    client = AsyncIOMotorClient(mongodb_url)
    database = client[app_settings.MONGODB_DATABASE]
    engine = AIOEngine(client=client, database=app_settings.MONGODB_DATABASE)
    app.state.client = client
    app.state.engine = engine
