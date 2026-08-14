import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import settings
from backend.catalog_data import CURATED_SOURCES_CATALOG

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

    # 1. Sources table with discover catalog fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        site_url TEXT,
        feed_url TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        best_for TEXT,
        why_read TEXT,
        adapter_type TEXT DEFAULT 'rss',
        enabled INTEGER DEFAULT 1,
        last_fetched_at TEXT
    );
    """)

    # Schema migration helper for existing databases
    cursor.execute("PRAGMA table_info(sources);")
    existing_cols = [col[1] for col in cursor.fetchall()]
    for col, col_type in [("site_url", "TEXT"), ("best_for", "TEXT"), ("why_read", "TEXT")]:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE sources ADD COLUMN {col} {col_type};")

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
        tags TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE SET NULL
    );
    """)

    # 3. FTS5 table
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
        id UNINDEXED,
        title,
        clean_content,
        publisher,
        tags
    );
    """)

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
        executive_tldr TEXT NOT NULL,
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
        key_takeaways TEXT NOT NULL,
        source_article_ids TEXT NOT NULL,
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
        chapters TEXT,
        transcript TEXT,
        published_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(dossier_id) REFERENCES dossiers(id) ON DELETE SET NULL
    );
    """)

    # Seed Curated Sources (Linux + Gaming) into Sources table
    for src in CURATED_SOURCES_CATALOG:
        cursor.execute("""
        INSERT INTO sources (id, name, site_url, feed_url, category, best_for, why_read, adapter_type, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'rss', ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            site_url = excluded.site_url,
            feed_url = excluded.feed_url,
            category = excluded.category,
            best_for = excluded.best_for,
            why_read = excluded.why_read;
        """, (
            src["id"], src["name"], src["site_url"], src["feed_url"],
            src["category"], src["best_for"], src["why_read"], src["enabled"]
        ))

    conn.commit()
    conn.close()
    logger.info(f"Database initialized with {len(CURATED_SOURCES_CATALOG)} curated publications across Linux and Gaming.")
