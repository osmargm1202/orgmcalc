"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from orgmcalc.db.connection import close_pool, init_pool
from orgmcalc.db.migrate import run_migrations

from .routes import (
    auth,
    calculos,
    docs,
    documentos,
    empresas,
    health,
    ingenieros,
    proyectos,
    storage,
    tipo_calculos,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs migrations and manages pool."""
    # Startup
    init_pool()
    run_migrations()
    yield
    # Shutdown
    await close_pool()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="orgmcalc",
        description="Shared calculations API for orgm projects",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(docs.router)
    app.include_router(auth.router)
    app.include_router(proyectos.router)
    app.include_router(empresas.router)
    app.include_router(ingenieros.router)
    app.include_router(documentos.router)
    app.include_router(calculos.router)
    app.include_router(tipo_calculos.router)
    app.include_router(storage.router)

    return app
