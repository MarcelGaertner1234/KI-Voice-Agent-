"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.config import get_settings
from api.middleware.logging import LoggingMiddleware
from api.middleware.security import SecurityHeadersMiddleware
from api.routers import auth, health, agents, calls, organizations, users
from api.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting VocalIQ API...")
    
    # Startup tasks
    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Initialize Weaviate client
    # TODO: Verify external service connections
    
    yield
    
    # Shutdown tasks
    logger.info("Shutting down VocalIQ API...")
    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Cleanup resources


def create_application() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    if settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(
        auth.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["authentication"]
    )
    app.include_router(
        users.router,
        prefix=f"{settings.API_V1_STR}/users",
        tags=["users"]
    )
    app.include_router(
        organizations.router,
        prefix=f"{settings.API_V1_STR}/organizations",
        tags=["organizations"]
    )
    app.include_router(
        agents.router,
        prefix=f"{settings.API_V1_STR}/agents",
        tags=["agents"]
    )
    app.include_router(
        calls.router,
        prefix=f"{settings.API_V1_STR}/calls",
        tags=["calls"]
    )
    
    # Setup Prometheus metrics
    if settings.PROMETHEUS_ENABLED:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )