import json
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.ingest.rss import run_all_ingestions

router = APIRouter(prefix="/api/articles", tags=["articles"])

@router.get("")
async def list_articles(
    category: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    conn = get_db_connection()
    cursor = conn.cursor()

    if q and q.strip():
        # FTS5 full text search query
        clean_q = q.strip().replace('"', '""')
        fts_term = f'"{clean_q}"*'
        cursor.execute("""
        SELECT a.id, a.source_id, a.title, a.url, a.author, a.publisher, a.published_at,
               a.summary, a.reading_time_minutes, a.signal_score, a.tags, a.created_at
        FROM articles_fts f
        JOIN articles a ON a.id = f.id
        WHERE articles_fts MATCH ?
        ORDER BY a.created_at DESC
        LIMIT ? OFFSET ?;
        """, (fts_term, limit, offset))
    elif category and category.lower() != "all":
        cursor.execute("""
        SELECT a.id, a.source_id, a.title, a.url, a.author, a.publisher, a.published_at,
               a.summary, a.reading_time_minutes, a.signal_score, a.tags, a.created_at
        FROM articles a
        JOIN sources s ON s.id = a.source_id
        WHERE s.category = ? OR a.tags LIKE ?
        ORDER BY a.created_at DESC
        LIMIT ? OFFSET ?;
        """, (category, f'%"{category}"%', limit, offset))
    else:
        cursor.execute("""
        SELECT id, source_id, title, url, author, publisher, published_at,
               summary, reading_time_minutes, signal_score, tags, created_at
        FROM articles
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?;
        """, (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    articles = []
    for r in rows:
        a = dict(r)
        a["tags"] = json.loads(a["tags"]) if a.get("tags") else []
        articles.append(a)

    return {"articles": articles, "count": len(articles)}

@router.get("/{article_id}")
async def get_article(article_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, source_id, title, url, author, publisher, published_at,
           clean_content, summary, reading_time_minutes, signal_score, tags, created_at
    FROM articles
    WHERE id = ?;
    """, (article_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Article not found")

    article = dict(row)
    article["tags"] = json.loads(article["tags"]) if article.get("tags") else []
    return article

@router.post("/ingest")
async def trigger_ingest():
    results = await run_all_ingestions()
    return results
