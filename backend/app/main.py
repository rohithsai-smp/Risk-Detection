"""
Digital Risk Shield - FastAPI Application Server
Enterprise Digital Risk Protection & Brand Impersonation Detection System
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .sample_data import seed_initial_data
from .routers import brands, social, apps, analyzer, threats, scan, reports, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    init_db()
    # Seed initial realistic demonstration threat data
    seed_initial_data()
    print("Digital Risk Shield DB initialized and seeded.")
    yield

app = FastAPI(
    title="Digital Risk Shield API",
    description="Digital Risk Protection & Brand Impersonation Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin integration (including Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://risk-detection-frontend.vercel.app",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(brands.router)
app.include_router(social.router)
app.include_router(apps.router)
app.include_router(analyzer.router)
app.include_router(threats.router)
app.include_router(scan.router)
app.include_router(reports.router)

# Health Check Endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Digital Risk Shield",
        "engine": "RapidFuzz Multi-Signal AI",
        "version": "1.0.0"
    }

# Mount Frontend Static Directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")

if os.path.exists(frontend_dir):
    # Mount css, js, etc.
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
    
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
        
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        # If static file exists, return it, otherwise fallback to index.html for SPA routing
        target = os.path.join(frontend_dir, full_path)
        if os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(frontend_dir, "index.html"))
