"""
CareerGraph AI backend — FastAPI application entrypoint.

Stage 1 wires up:
  * FastAPI app + CORS (for a local React dev frontend)
  * Global exception handling / logging
  * /api/careers routes (including the priority endpoint:
    POST /api/careers/analyze)
  * Health check

Later stages add: auth, profile, jobs, analysis, roadmap, resources.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.careers import router as careers_router
from app.api.profile import router as profile_router
from app.api.resources import router as resources_router
from app.api.roadmap import router as roadmap_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging, get_logger
from app.database.session import init_db
from app.services.serpapi_service import SerpApiError

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # MVP: create tables if they don't exist yet (no migrations framework
    # for this hackathon build -- see README "Known limitations").
    init_db()
    logger.info("Database tables ready.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time career intelligence platform powered by SerpApi.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SerpApiError)
async def serpapi_error_handler(request: Request, exc: SerpApiError) -> JSONResponse:
    logger.error("Unhandled SerpApiError on %s: %s", request.url.path, exc.message)
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": f"Upstream SerpApi error: {exc.message}"},
    )


@app.get("/", tags=["health"])
async def root() -> dict:
    return {"service": settings.APP_NAME, "status": "ok"}


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "serpapi_configured": bool(settings.SERPAPI_API_KEY),
    }


app.include_router(careers_router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)
app.include_router(roadmap_router, prefix=settings.API_V1_PREFIX)
app.include_router(resources_router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
