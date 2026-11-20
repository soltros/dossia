import time
import hashlib
from urllib.parse import urlsplit
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.config import settings
from backend.hermes.client import LLMClient

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SourceItem(BaseModel):
    name: str
    feed_url: str
    category: str

class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    hermes_base_url: Optional[str] = None
    hermes_api_key: Optional[str] = None
    hermes_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    chatgpt_model: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    anthropic_model: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    custom_base_url: Optional[str] = None
    custom_api_key: Optional[str] = None
    custom_model: Optional[str] = None
    podcast_base_url: Optional[str] = None

class ProviderTestRequest(BaseModel):
    provider: Optional[str] = None

ALLOWED_PROVIDERS = {"hermes", "openai", "chatgpt", "anthropic", "openrouter", "custom"}

def _mask_key(k: str) -> str:
    return "Configured" if k else ""

@router.get("")
async def get_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, feed_url, category, enabled, last_fetched_at FROM sources;")
    sources = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {
        "llm_provider": settings.llm_provider,
        "hermes_base_url": settings.hermes_base_url,
        "hermes_model": settings.hermes_model,
        "hermes_api_key_masked": _mask_key(settings.hermes_api_key),
        "openai_model": settings.openai_model,
        "openai_api_key_masked": _mask_key(settings.openai_api_key),
        "chatgpt_model": settings.chatgpt_model,
        "anthropic_model": settings.anthropic_model,
        "anthropic_api_key_masked": _mask_key(settings.anthropic_api_key),
        "openrouter_model": settings.openrouter_model,
        "openrouter_api_key_masked": _mask_key(settings.openrouter_api_key),
        "custom_base_url": settings.custom_base_url,
        "custom_model": settings.custom_model,
        "custom_api_key_masked": _mask_key(settings.custom_api_key),
        "podcast_base_url": settings.podcast_base_url,
        "sources": sources
    }

@router.post("")
async def update_settings(payload: SettingsUpdate):
    if payload.llm_provider is not None:
        provider = payload.llm_provider.strip().lower()
        if provider not in ALLOWED_PROVIDERS:
            raise HTTPException(status_code=422, detail="Unsupported LLM provider")
        settings.llm_provider = provider
    if payload.hermes_base_url is not None:
        settings.hermes_base_url = payload.hermes_base_url
    if payload.hermes_api_key is not None and payload.hermes_api_key != "":
        settings.hermes_api_key = payload.hermes_api_key
    if payload.hermes_model is not None:
        settings.hermes_model = payload.hermes_model

    if payload.openai_api_key is not None and payload.openai_api_key != "":
        settings.openai_api_key = payload.openai_api_key
    if payload.openai_model is not None:
        settings.openai_model = payload.openai_model
    if payload.chatgpt_model is not None:
        settings.chatgpt_model = payload.chatgpt_model

    if payload.anthropic_api_key is not None and payload.anthropic_api_key != "":
        settings.anthropic_api_key = payload.anthropic_api_key
    if payload.anthropic_model is not None:
        settings.anthropic_model = payload.anthropic_model

    if payload.openrouter_api_key is not None and payload.openrouter_api_key != "":
        settings.openrouter_api_key = payload.openrouter_api_key
    if payload.openrouter_model is not None:
        settings.openrouter_model = payload.openrouter_model

    if payload.custom_base_url is not None:
        settings.custom_base_url = payload.custom_base_url
    if payload.custom_api_key is not None and payload.custom_api_key != "":
        settings.custom_api_key = payload.custom_api_key
    if payload.custom_model is not None:
        settings.custom_model = payload.custom_model

    if payload.podcast_base_url is not None:
        settings.podcast_base_url = payload.podcast_base_url

    # Persist changes
    settings.save_persisted()

    return {"status": "success", "message": "Settings updated and persisted successfully"}

@router.post("/test-llm")
async def test_llm_connection(payload: ProviderTestRequest):
    """Health check test query against the configured or requested LLM provider."""
    provider = (payload.provider or settings.llm_provider).strip().lower()
    if provider not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=422, detail="Unsupported LLM provider")
    client = LLMClient(provider=provider)
    start_time = time.time()
    
    test_messages = [
        {"role": "system", "content": "You are a test probe."},
        {"role": "user", "content": "Respond with the single word: OK"}
    ]
    
    try:
        resp = await client.generate_chat_completion(test_messages, temperature=0.1)
    except (RuntimeError, httpx.HTTPError) as exc:
        duration = round((time.time() - start_time) * 1000, 1)
        return {"status": "offline_or_fallback", "provider": client.provider, "latency_ms": duration, "message": str(exc)}
    duration = round((time.time() - start_time) * 1000, 1)
    
    if resp and len(resp.strip()) > 0:
        return {
            "status": "connected",
            "provider": client.provider,
            "latency_ms": duration,
            "response": resp.strip()[:100]
        }
    else:
        return {
            "status": "offline_or_fallback",
            "provider": client.provider,
            "latency_ms": duration,
            "message": f"Provider {client.provider} returned empty response or is unreachable. Local domain synthesis will be used."
        }

@router.post("/sources")
async def add_source(source: SourceItem):
    name = source.name.strip()
    feed_url = source.feed_url.strip()
    category = source.category.strip()
    parsed_url = urlsplit(feed_url)
    if not name or not category or parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise HTTPException(status_code=422, detail="Provide a source name, category, and valid HTTP(S) feed URL")
    source_id = hashlib.sha256(feed_url.encode()).hexdigest()[:12]
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO sources (id, name, feed_url, category, enabled)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(id) DO UPDATE SET name=excluded.name, feed_url=excluded.feed_url,
          category=excluded.category, enabled=1;
        """, (source_id, name, feed_url, category))
        conn.commit()
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=409, detail="Could not add source; this feed URL may already be registered")
    finally:
        conn.close()
    return {"status": "success", "source_id": source_id}

@router.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Source not found")
        conn.commit()
    finally:
        conn.close()
    return {"status": "success", "source_id": source_id}
