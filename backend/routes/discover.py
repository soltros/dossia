from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.database import get_db_connection

router = APIRouter(prefix="/api/discover", tags=["discover"])

class ToggleRequest(BaseModel):
    enabled: bool

@router.get("")
async def get_discover_catalog():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, site_url, feed_url, category, best_for, why_read, enabled, last_fetched_at
    FROM sources
    ORDER BY category ASC, name ASC;
    """)
    rows = cursor.fetchall()
    conn.close()

    sources = [dict(r) for r in rows]
    
    # Collect categories
    categories = sorted(list(set(s["category"] for s in sources)))

    return {
        "categories": categories,
        "sources": sources,
        "total": len(sources),
        "followed_count": sum(1 for s in sources if s["enabled"] == 1)
    }

@router.post("/{source_id}/toggle")
async def toggle_source(source_id: str, payload: ToggleRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE sources
    SET enabled = ?
    WHERE id = ?;
    """, (1 if payload.enabled else 0, source_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Source not found")
        
    conn.commit()
    conn.close()
    return {"status": "success", "source_id": source_id, "enabled": payload.enabled}

@router.post("/batch")
async def batch_toggle(enabled: bool = True, category: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if category and category.lower() != "all":
        cursor.execute("UPDATE sources SET enabled = ? WHERE category = ?", (1 if enabled else 0, category))
    else:
        cursor.execute("UPDATE sources SET enabled = ?", (1 if enabled else 0,))
    
    conn.commit()
    conn.close()
    return {"status": "success", "enabled": enabled}
