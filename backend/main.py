from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings

from app.api.routes import reports, voice_router

from app.api.routes import (
    auth,
    projects,
    input,
    planner,
    stages,
    validation,
    # ra_system,  # Disabled: HuggingFace network issue
    architecture,
    nexus,
    aidude,
    code_generation,
    export,
    version,
    activity,
    reports,
    knowledge,
    admin,
    sharing,
    employees
)
from app.api.middleware.request_logging import RequestLoggingMiddleware
from app.api.middleware.error_handler import setup_exception_handlers
from app.utils.custom_logger import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(employees.router, prefix="/api", tags=["Employees"])
app.include_router(sharing.router, prefix="/api", tags=["Sharing"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(input.router, prefix="/api/input", tags=["Input"])
app.include_router(planner.router, prefix="/api/planner", tags=["Planner"])
app.include_router(stages.router, prefix="/api/stage", tags=["Stages"])
app.include_router(validation.router, prefix="/api/validation", tags=["Validation"])
# app.include_router(ra_system.router, prefix="/api/ra", tags=["RA System"])  # Disabled: HuggingFace network issue
app.include_router(architecture.router, prefix="/api/architecture", tags=["Architecture"])
app.include_router(nexus.router, prefix="/api/nexus", tags=["Nexus AI"])
app.include_router(aidude.router, prefix="/api/aidude", tags=["AI Dude"])
app.include_router(code_generation.router, prefix="/api/code", tags=["Code Generation"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(version.router, prefix="/api/version", tags=["Version Control"])
app.include_router(activity.router, prefix="/api/activity", tags=["Activity"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])

# Mount static files for manuals
import os
manuals_path = os.path.join(os.path.dirname(__file__), "..", "data", "manuals", "display_manuals")
if os.path.exists(manuals_path):
    app.mount("/manuals", StaticFiles(directory=manuals_path), name="manuals")


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )