import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings, STATIC_DIR, MEDIA_DIR
from backend.database import init_db
from backend.ingest.rss import run_all_ingestions
from backend.routes.dossiers import router as dossiers_router
from backend.routes.articles import router as articles_router
from backend.routes.podcast import router as podcast_router
from backend.routes.hermes import router as hermes_router
from backend.routes.settings import router as settings_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dossia")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and initial ingestion
    logger.info("Initializing Dossia database...")
    init_db()
    
    # Run initial ingestion in background if db has few articles
    try:
        from backend.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles;")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            logger.info("Database empty, initiating first high-signal feed ingestion...")
            await run_all_ingestions()
    except Exception as e:
        logger.warning(f"Initial feed ingestion encountered issue: {e}")
        
    yield
    logger.info("Dossia server shutting down.")

app = FastAPI(
    title="Dossia API",
    description="Autonomous News Intelligence, Editorial Dossiers & Podcasting 2.0 Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse

# Register API Routers
app.include_router(dossiers_router)
app.include_router(articles_router)
app.include_router(podcast_router)
app.include_router(hermes_router)
app.include_router(settings_router)

# Mount audio media files
app.mount("/audio", StaticFiles(directory=str(MEDIA_DIR)), name="audio")

# Mount frontend static directory for /static/* assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(STATIC_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
