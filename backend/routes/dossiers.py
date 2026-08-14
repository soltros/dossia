import json
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.hermes.synthesizer import generate_daily_dossier

router = APIRouter(prefix="/api/dossiers", tags=["dossiers"])

@router.get("/latest")
async def get_latest_dossier():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, edition_date, edition_type, title, executive_tldr, created_at
    FROM dossiers
    ORDER BY created_at DESC
    LIMIT 1;
    """)
    dossier_row = cursor.fetchone()

    if not dossier_row:
        conn.close()
        # Automatically generate the first inaugural dossier
        new_dossier = await generate_daily_dossier(edition_type="morning")
        return new_dossier

    dossier = dict(dossier_row)
    dossier["executive_tldr"] = json.loads(dossier["executive_tldr"])

    # Fetch story clusters
    cursor.execute("""
    SELECT id, headline, category, narrative_summary, key_takeaways, source_article_ids, signal_badge, sort_order
    FROM story_clusters
    WHERE dossier_id = ?
    ORDER BY sort_order ASC;
    """, (dossier["id"],))
    
    clusters = []
    for c_row in cursor.fetchall():
        c = dict(c_row)
        c["key_takeaways"] = json.loads(c["key_takeaways"])
        source_ids = json.loads(c["source_article_ids"])
        
        # Hydrate source articles
        sources = []
        if source_ids:
            placeholders = ",".join(["?"] * len(source_ids))
            cursor.execute(f"""
            SELECT id, title, url, publisher, author, published_at, reading_time_minutes, signal_score
            FROM articles
            WHERE id IN ({placeholders})
            """, source_ids)
            sources = [dict(r) for r in cursor.fetchall()]

        c["sources"] = sources
        clusters.append(c)

    dossier["story_clusters"] = clusters
    conn.close()
    return dossier

@router.get("")
async def list_dossiers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, edition_date, edition_type, title, executive_tldr, created_at
    FROM dossiers
    ORDER BY created_at DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    
    dossiers = []
    for r in rows:
        d = dict(r)
        d["executive_tldr"] = json.loads(d["executive_tldr"])
        dossiers.append(d)
    return dossiers

@router.post("/generate")
async def trigger_dossier_generation(edition_type: str = "morning"):
    dossier = await generate_daily_dossier(edition_type=edition_type)
    return {"status": "success", "dossier": dossier}
