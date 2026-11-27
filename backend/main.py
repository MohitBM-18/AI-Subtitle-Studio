"""
AI Subtitle Studio – FastAPI Application Entry Point
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.config import settings
from backend.routes import upload, transcription, translation, rendering, jobs

# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Subtitle Studio",
    description="AI-powered video subtitle generation, translation & permanent embedding",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(upload.router,        prefix="/api", tags=["upload"])
app.include_router(transcription.router, prefix="/api", tags=["transcription"])
app.include_router(translation.router,   prefix="/api", tags=["translation"])
app.include_router(rendering.router,     prefix="/api", tags=["rendering"])
app.include_router(jobs.router,          prefix="/api", tags=["jobs"])

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}

# ── Serve frontend static files ───────────────────────────────────────────────
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/{page}.html", include_in_schema=False)
    async def serve_page(page: str):
        p = frontend_dir / f"{page}.html"
        if p.exists():
            return FileResponse(str(p))
        return FileResponse(str(frontend_dir / "index.html"))

# ── Dev entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
