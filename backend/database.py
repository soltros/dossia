import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import settings

logger = logging.getLogger("dossia.db")

CURATED_LINUX_CATALOG = [
    {
        "id": "phoronix",
        "name": "Phoronix",
        "site_url": "https://www.phoronix.com/",
        "feed_url": "https://www.phoronix.com/rss.php",
        "category": "Hardware & Kernel Benchmarks",
        "best_for": "Hardware benchmarks, GPU/Vulkan drivers, and low-level Linux performance.",
        "why_read": "Michael Larabel tracks patch submissions, GPU/Vulkan drivers, kernel optimization work, and runs rigorous automated benchmarks on modern hardware.",
        "enabled": 1
    },
    {
        "id": "lwn",
        "name": "LWN.net (Linux Weekly News)",
        "site_url": "https://lwn.net/",
        "feed_url": "https://lwn.net/headlines/rss",
        "category": "Kernel & Deep Architecture",
        "best_for": "Deep, technical journalism on kernel architecture and developer mailing lists.",
        "why_read": "Unmatched in technical depth. Covers architectural decisions, security patches, and maintainer debates happening inside the Linux kernel and core toolchains.",
        "enabled": 1
    },
    {
        "id": "itsfoss",
        "name": "It's FOSS",
        "site_url": "https://itsfoss.com/",
        "feed_url": "https://itsfoss.com/rss/",
        "category": "Desktop & Open Source",
        "best_for": "General desktop Linux news, open-source project spotlights, and guides.",
        "why_read": "Covers daily news around major desktop environments, newly released open-source utilities, and straightforward distro updates.",
        "enabled": 1
    },
    {
        "id": "9to5linux",
        "name": "9to5Linux",
        "site_url": "https://9to5linux.com/",
        "feed_url": "https://9to5linux.com/feed",
        "category": "Distro Releases & Updates",
        "best_for": "Fast-paced distribution releases, kernel version drops, and software updates.",
        "why_read": "Quick turnaround on new release announcements for popular distros (Fedora, Arch, Debian, Ubuntu) and desktop environments (KDE Plasma, GNOME, COSMIC).",
        "enabled": 1
    },
    {
        "id": "omgubuntu",
        "name": "OMG! Ubuntu!",
        "site_url": "https://www.omgubuntu.co.uk/",
        "feed_url": "https://www.omgubuntu.co.uk/feed",
        "category": "Desktop & GNOME",
        "best_for": "Ubuntu ecosystem, GNOME developments, and desktop app updates.",
        "why_read": "Joey Sneddon covers cross-distro desktop topics, GTK/GNOME app updates, and Linux ecosystem news.",
        "enabled": 1
    },
    {
        "id": "gamingonlinux",
        "name": "GamingOnLinux",
        "site_url": "https://www.gamingonlinux.com/",
        "feed_url": "https://www.gamingonlinux.com/article_rss.php",
        "category": "Gaming & Graphics Stack",
        "best_for": "Proton/Wine compatibility, Steam on Linux, native game releases, and Mesa/Vulkan progress.",
        "why_read": "Liam Dawe covers the rapid pace of Linux gaming, graphics driver progress (Mesa/Vulkan), and portable PC gaming ecosystems.",
        "enabled": 1
    },
    {
        "id": "distrowatch",
        "name": "DistroWatch Weekly",
        "site_url": "https://distrowatch.com/",
        "feed_url": "https://distrowatch.com/news/dww.xml",
        "category": "Distros & Packages",
        "best_for": "Tracking all active distributions, package changes, and new project releases.",
        "why_read": "Summarizes major ecosystem announcements, release schedules, package migrations, and community reviews.",
        "enabled": 1
    },
    {
        "id": "nixcraft",
        "name": "nixCraft",
        "site_url": "https://www.cyberciti.biz/",
        "feed_url": "https://www.cyberciti.biz/feed/",
        "category": "Sysadmin & Security",
        "best_for": "System administrators, DevOps workflows, shell tips, and security alerts.",
        "why_read": "Vivek Gite focuses on practical sysadmin work, containerization, server security vulnerabilities, and command-line tooling.",
        "enabled": 1
    },
    {
        "id": "linuxtoday",
        "name": "Linux Today",
        "site_url": "https://www.linuxtoday.com/",
        "feed_url": "https://www.linuxtoday.com/feed/",
        "category": "FOSS News Aggregation",
        "best_for": "Daily curated news aggregation across the entire FOSS world.",
        "why_read": "Acts as a central feed pulling together security advisories, enterprise open-source news, tutorials, and distro release notes.",
        "enabled": 1
    },
    {
        "id": "linuxuprising",
        "name": "Linux Uprising",
        "site_url": "https://www.linuxuprising.com/",
        "feed_url": "https://feeds.feedburner.com/LinuxUprising",
        "category": "Utilities & CLI Tools",
        "best_for": "App reviews, small utility discovery, command-line tweaks, and PPA/Flatpak highlights.",
        "why_read": "Great for discovering niche open-source utilities, terminal tools, and detailed installation/configuration recipes.",
        "enabled": 1
    }
]

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

    # Seed Curated Linux Sources into Sources table
    for src in CURATED_LINUX_CATALOG:
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
    logger.info("Database initialized with curated Linux Discover Catalog.")
