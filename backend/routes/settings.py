from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.config import settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SourceItem(BaseModel):
    name: str
    feed_url: str
    category: str

class SettingsUpdate(BaseModel):
    hermes_base_url: Optional[str] = None
    hermes_api_key: Optional[str] = None
    hermes_model: Optional[str] = None
    podcast_base_url: Optional[str] = None

@router.get("")
async def get_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, feed_url, category, enabled, last_fetched_at FROM sources;")
    sources = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {
        "hermes_base_url": settings.hermes_base_url,
        "hermes_model": settings.hermes_model,
        "podcast_base_url": settings.podcast_base_url,
        "sources": sources
    }

@router.post("")
async def update_settings(payload: SettingsUpdate):
    if payload.hermes_base_url is not None:
        settings.hermes_base_url = payload.hermes_base_url
    if payload.hermes_api_key is not None:
        settings.hermes_api_key = payload.hermes_api_key
    if payload.hermes_model is not None:
        settings.hermes_model = payload.hermes_model
    if payload.podcast_base_url is not None:
        settings.podcast_base_url = payload.podcast_base_url

    return {"status": "success", "settings": {
        "hermes_base_url": settings.hermes_base_url,
        "hermes_model": settings.hermes_model,
        "podcast_base_url": settings.podcast_base_url
    }}

@router.post("/sources")
async def add_source(source: SourceItem):
    import hashlib
    source_id = hashlib.sha256(source.feed_url.encode()).hexdigest()[:12]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO sources (id, name, feed_url, category, enabled)
    VALUES (?, ?, ?, ?, 1);
    """, (source_id, source.name, source.feed_url, source.category))
    conn.commit()
    conn.close()
    return {"status": "success", "source_id": source_id}

@router.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}
