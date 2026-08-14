import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
import feedparser
from backend.ingest.cleaner import clean_html_to_markdown, calculate_reading_time
from backend.database import get_db_connection

logger = logging.getLogger("dossia.ingest")

async def fetch_full_article_content(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Attempts to fetch the full page body if the RSS feed content is truncated."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 (Dossia Editorial Bot)"
        }
        resp = await client.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        logger.debug(f"Could not fetch full article page from {url}: {e}")
    return None

async def ingest_feed(source_id: str, feed_url: str, category: str, default_publisher: str) -> int:
    """Fetches and processes an RSS / Atom feed into clean articles in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_articles_count = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0 (Dossia News Reader)"
    }
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(feed_url, follow_redirects=True)
            if resp.status_code != 200:
                logger.warning(f"Failed to fetch feed {feed_url}: status {resp.status_code}")
                return 0

            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:20]: # Process top 20 latest entries
                title = entry.get("title", "").strip()
                url = entry.get("link", "").strip()
                if not title or not url:
                    continue

                # Check if article already exists
                cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
                if cursor.fetchone():
                    continue

                author = entry.get("author", "") or entry.get("creator", "") or default_publisher
                published = entry.get("published", "") or entry.get("updated", "") or datetime.utcnow().isoformat()
                
                # Raw content from feed entry
                raw_html = ""
                if "content" in entry and len(entry.content) > 0:
                    raw_html = entry.content[0].get("value", "")
                elif "summary" in entry:
                    raw_html = entry.summary
                elif "description" in entry:
                    raw_html = entry.description

                clean_markdown = clean_html_to_markdown(raw_html)

                # If the RSS entry was severely truncated (< 120 words), attempt full page extraction
                if len(clean_markdown.split()) < 120:
                    full_html = await fetch_full_article_content(client, url)
                    if full_html:
                        extracted = clean_html_to_markdown(full_html)
                        if len(extracted.split()) > len(clean_markdown.split()):
                            clean_markdown = extracted

                reading_time = calculate_reading_time(clean_markdown)
                article_id = hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]
                
                tags = [category]
                if "tags" in entry:
                    tags.extend([t.term for t in entry.tags if hasattr(t, "term")])
                
                summary_preview = clean_markdown[:280] + "..." if len(clean_markdown) > 280 else clean_markdown

                cursor.execute("""
                INSERT OR IGNORE INTO articles (
                    id, source_id, title, url, author, publisher, published_at,
                    clean_content, summary, reading_time_minutes, signal_score, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_id,
                    source_id,
                    title,
                    url,
                    author,
                    default_publisher,
                    published,
                    clean_markdown,
                    summary_preview,
                    reading_time,
                    8.5, # Default high signal score
                    json.dumps(tags[:5])
                ))
                new_articles_count += 1

            cursor.execute("UPDATE sources SET last_fetched_at = CURRENT_TIMESTAMP WHERE id = ?", (source_id,))
            conn.commit()

    except Exception as e:
        logger.error(f"Error ingesting feed {feed_url}: {e}")
    finally:
        conn.close()

    return new_articles_count

async def run_all_ingestions() -> Dict[str, Any]:
    """Runs ingestion across all enabled sources in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, feed_url, category FROM sources WHERE enabled = 1;")
    sources = cursor.fetchall()
    conn.close()

    total_ingested = 0
    results = []

    for src in sources:
        count = await ingest_feed(src["id"], src["feed_url"], src["category"], src["name"])
        total_ingested += count
        results.append({"source": src["name"], "new_articles": count})

    return {
        "status": "success",
        "total_new_articles": total_ingested,
        "sources_processed": len(sources),
        "details": results
    }
