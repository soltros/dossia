import os
import logging
import asyncio
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
from backend.routes.discover import router as discover_router
from backend.routes.chatgpt_auth import router as chatgpt_auth_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dossia")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and initial ingestion
    logger.info("Initializing Dossia database...")
    init_db()
    
    # Schedule initial ingestion without holding the HTTP server's startup open.
    ingestion_task = None
    try:
        from backend.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles;")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            logger.info("Database empty, initiating first high-signal feed ingestion...")
            ingestion_task = asyncio.create_task(run_all_ingestions(), name="initial-feed-ingestion")
            def log_ingestion_result(task):
                if task.cancelled():
                    return
                error = task.exception()
                if error:
                    logger.warning("Initial feed ingestion failed: %s", error)
                else:
                    logger.info("Initial feed ingestion finished: %s", task.result())
            ingestion_task.add_done_callback(log_ingestion_result)
    except Exception as e:
        logger.warning(f"Initial feed ingestion encountered issue: {e}")
        
    yield
    if ingestion_task and not ingestion_task.done():
        ingestion_task.cancel()
        try:
            await ingestion_task
        except asyncio.CancelledError:
            pass
    logger.info("Dossia server shutting down.")

app = FastAPI(
    title="Dossia API",
    description="Autonomous News Intelligence, Editorial Dossiers & Podcasting 2.0 Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv(
        "DOSSIA_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",") if origin.strip()],
    allow_credentials=False,
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
app.include_router(discover_router)
app.include_router(chatgpt_auth_router)

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
    uvicorn.run("backend.main:app", host=os.getenv("DOSSIA_HOST", "127.0.0.1"), port=int(os.getenv("DOSSIA_PORT", "8000")), reload=True)
