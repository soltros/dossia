import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import settings

logger = logging.getLogger("dossia.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Sources table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        feed_url TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        adapter_type TEXT DEFAULT 'rss',
        enabled INTEGER DEFAULT 1,
        last_fetched_at TEXT
    );
    """)

    # 2. Articles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        source_id TEXT,
        title TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        author TEXT,
        publisher TEXT,
        published_at TEXT,
        clean_content TEXT,
        summary TEXT,
        reading_time_minutes INTEGER DEFAULT 3,
        signal_score REAL DEFAULT 5.0,
        tags TEXT, -- JSON array
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE SET NULL
    );
    """)

    # 3. Full-Text Search (FTS5) table for articles
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
        id UNINDEXED,
        title,
        clean_content,
        publisher,
        tags
    );
    """)

    # Triggers to keep FTS5 synchronized with articles table
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
        INSERT INTO articles_fts(id, title, clean_content, publisher, tags)
        VALUES (new.id, new.title, new.clean_content, new.publisher, new.tags);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
        DELETE FROM articles_fts WHERE id = old.id;
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
        DELETE FROM articles_fts WHERE id = old.id;
        INSERT INTO articles_fts(id, title, clean_content, publisher, tags)
        VALUES (new.id, new.title, new.clean_content, new.publisher, new.tags);
    END;
    """)

    # 4. Dossiers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dossiers (
        id TEXT PRIMARY KEY,
        edition_date TEXT NOT NULL,
        edition_type TEXT DEFAULT 'morning',
        title TEXT NOT NULL,
        executive_tldr TEXT NOT NULL, -- JSON array of bullet strings
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Story Clusters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS story_clusters (
        id TEXT PRIMARY KEY,
        dossier_id TEXT NOT NULL,
        headline TEXT NOT NULL,
        category TEXT NOT NULL,
        narrative_summary TEXT NOT NULL,
        key_takeaways TEXT NOT NULL, -- JSON array
        source_article_ids TEXT NOT NULL, -- JSON array
        signal_badge TEXT DEFAULT 'High Signal',
        sort_order INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(dossier_id) REFERENCES dossiers(id) ON DELETE CASCADE
    );
    """)

    # 6. Podcast Episodes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podcast_episodes (
        id TEXT PRIMARY KEY,
        dossier_id TEXT,
        episode_number INTEGER UNIQUE,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        audio_url TEXT,
        duration_seconds INTEGER DEFAULT 0,
        chapters TEXT, -- JSON array of {title, start_seconds}
        transcript TEXT,
        published_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(dossier_id) REFERENCES dossiers(id) ON DELETE SET NULL
    );
    """)

    # 7. Seed Default Curated High-Signal Sources if empty
    cursor.execute("SELECT COUNT(*) FROM sources;")
    if cursor.fetchone()[0] == 0:
        default_sources = [
            ("hn-best", "Hacker News Top Signals", "https://news.ycombinator.com/rss", "Engineering", "hackernews", 1),
            ("cloudflare-blog", "Cloudflare Engineering", "http://blog.cloudflare.com/rss/", "Systems & Cloud", "rss", 1),
            ("simon-willison", "Simon Willison's Weblog (AI & Web)", "https://simonwillison.net/atom/everything/", "AI & Web", "rss", 1),
            ("github-blog", "GitHub Engineering Blog", "https://github.blog/engineering/feed/", "Dev Tools", "rss", 1),
            ("arxiv-ai", "arXiv AI & Machine Learning", "http://export.arxiv.org/rss/cs.AI", "Research", "rss", 1),
            ("dan-luu", "Dan Luu Systems & Hardware", "https://danluu.com/atom.xml", "Systems & Hardware", "rss", 1),
            ("fly-io", "Fly.io Architecture & Phoenix", "https://fly.io/blog/feed.xml", "Distributed Systems", "rss", 1),
            ("mit-tech-review", "MIT Tech Review Insights", "https://www.technologyreview.com/feed/", "Science & DeepTech", "rss", 1)
        ]
        cursor.executemany("""
        INSERT INTO sources (id, name, feed_url, category, adapter_type, enabled)
        VALUES (?, ?, ?, ?, ?, ?);
        """, default_sources)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully with FTS5 and default sources.")
