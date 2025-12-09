import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_mcp import FastApiMCP
from starlette.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging


def custom_generate_unique_id(route: APIRoute) -> str:
    return route.name

setup_logging()
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Provides a context manager for managing the lifespan of a FastAPI application.

    Inside the `lifespan` context manager, the `before start` and `before stop`
    comments indicate where the startup and shutdown operations should be
    implemented.
    """

    # before start
    logger.info("Server starting up...")
    yield
    logger.info("Server shutting down...")
    # before stop

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json", # API_ENDPOINT: http://127.0.0.1:8000/docs  OPENAPI URL: http://127.0.0.1:8000/api/v1/openapi.json
    generate_unique_id_function=custom_generate_unique_id
)

@app.get("/")
async def project_info():
    return {
        "message": "Talk 2 Book Project"
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

mcp =FastApiMCP(app, name="Talk2Book project")
mcp.mount_http()
