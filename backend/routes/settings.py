import time
from fastapi import APIRouter
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
    anthropic_api_key: Optional[str] = None
    anthropic_model: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    custom_base_url: Optional[str] = None
    custom_api_key: Optional[str] = None
    custom_model: Optional[str] = None
    podcast_base_url: Optional[str] = None

def _mask_key(k: str) -> str:
    if not k:
        return ""
    if len(k) <= 8:
        return "********"
    return f"{k[:4]}...{k[-4:]}"

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
        settings.llm_provider = payload.llm_provider
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
async def test_llm_connection(provider: Optional[str] = None):
    """Health check test query against the configured or requested LLM provider."""
    client = LLMClient(provider=provider or settings.llm_provider)
    start_time = time.time()
    
    test_messages = [
        {"role": "system", "content": "You are a test probe."},
        {"role": "user", "content": "Respond with the single word: OK"}
    ]
    
    resp = await client.generate_chat_completion(test_messages, temperature=0.1)
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
