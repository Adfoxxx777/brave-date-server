"""The main module"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
import logging
from typing import Dict
import uvicorn

from app.auth import router as auth_router
from app.config import settings
from app.matches import router as matches_router
from app.messages import router as messages_router
from app.users import router as users_router
from app.utils import engine
from app.websockets import router as websockets_router

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@lru_cache()
def get_app() -> FastAPI:
    """
    A method that creates, configures and returns a FastAPI app instance

    Return:
        FastAPI : a FastAPI app instance
    """
    app_settings = settings()
    app = FastAPI(
        docs_url="/docs",
        redoc_url="/redocs",
        title="Brave Date Server",
        description="The server side of Brave Date.",
        version="0.1.0",
        openapi_url="/api/v1/openapi.json",
    )

    origins = [
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    origins.extend(app_settings.cors_origins)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup() -> None:
        logger.info("Connecting to MongoDB...")
        await engine.init_engine_app(app)
        logger.info("Connected to MongoDB!")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        logger.info("Closing connection with MongoDB...")
        try:
            await app.state.client.close()
        except Exception as err:
            logger.error(repr(err))
        logger.info("Closed connection with MongoDB!")

    @app.get("/api")
    async def root() -> Dict[str, str]:
        return {"message": "Welcome to the Brave Date Server."}

    app.include_router(auth_router.router, tags=["auth"])
    app.include_router(users_router.router, tags=["users"])
    app.include_router(matches_router.router, tags=["matches"])
    app.include_router(messages_router.router, tags=["messages"])
    app.include_router(websockets_router.router, tags=["websockets"])

    return app

tinder_app = get_app()

def serve() -> None:
    """
    A method that runs a uvicorn server.
    """
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:tinder_app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    serve()
