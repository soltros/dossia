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
        "category": "Linux: Hardware & Benchmarks",
        "best_for": "Hardware benchmarks, GPU/Vulkan drivers, and low-level Linux performance.",
        "why_read": "Michael Larabel tracks patch submissions, GPU/Vulkan drivers, kernel optimization work, and runs rigorous automated benchmarks on modern hardware.",
        "enabled": 1
    },
    {
        "id": "lwn",
        "name": "LWN.net (Linux Weekly News)",
        "site_url": "https://lwn.net/",
        "feed_url": "https://lwn.net/headlines/rss",
        "category": "Linux: Kernel & Architecture",
        "best_for": "Deep, technical journalism on kernel architecture and developer mailing lists.",
        "why_read": "Unmatched in technical depth. Covers architectural decisions, security patches, and maintainer debates happening inside the Linux kernel and core toolchains.",
        "enabled": 1
    },
    {
        "id": "itsfoss",
        "name": "It's FOSS",
        "site_url": "https://itsfoss.com/",
        "feed_url": "https://itsfoss.com/rss/",
        "category": "Linux: Desktop & Open Source",
        "best_for": "General desktop Linux news, open-source project spotlights, and guides.",
        "why_read": "Covers daily news around major desktop environments, newly released open-source utilities, and straightforward distro updates.",
        "enabled": 1
    },
    {
        "id": "9to5linux",
        "name": "9to5Linux",
        "site_url": "https://9to5linux.com/",
        "feed_url": "https://9to5linux.com/feed",
        "category": "Linux: Distro Releases",
        "best_for": "Fast-paced distribution releases, kernel version drops, and software updates.",
        "why_read": "Quick turnaround on new release announcements for popular distros (Fedora, Arch, Debian, Ubuntu) and desktop environments (KDE Plasma, GNOME, COSMIC).",
        "enabled": 1
    },
    {
        "id": "omgubuntu",
        "name": "OMG! Ubuntu!",
        "site_url": "https://www.omgubuntu.co.uk/",
        "feed_url": "https://www.omgubuntu.co.uk/feed",
        "category": "Linux: Desktop & GNOME",
        "best_for": "Ubuntu ecosystem, GNOME developments, and desktop app updates.",
        "why_read": "Joey Sneddon covers cross-distro desktop topics, GTK/GNOME app updates, and Linux ecosystem news.",
        "enabled": 1
    },
    {
        "id": "gamingonlinux",
        "name": "GamingOnLinux",
        "site_url": "https://www.gamingonlinux.com/",
        "feed_url": "https://www.gamingonlinux.com/article_rss.php",
        "category": "Linux: Gaming & Graphics",
        "best_for": "Proton/Wine compatibility, Steam on Linux, native game releases, and Mesa/Vulkan progress.",
        "why_read": "Liam Dawe covers the rapid pace of Linux gaming, graphics driver progress (Mesa/Vulkan), and portable PC gaming ecosystems.",
        "enabled": 1
    },
    {
        "id": "distrowatch",
        "name": "DistroWatch Weekly",
        "site_url": "https://distrowatch.com/",
        "feed_url": "https://distrowatch.com/news/dww.xml",
        "category": "Linux: Distros & Packages",
        "best_for": "Tracking all active distributions, package changes, and new project releases.",
        "why_read": "Summarizes major ecosystem announcements, release schedules, package migrations, and community reviews.",
        "enabled": 1
    },
    {
        "id": "nixcraft",
        "name": "nixCraft",
        "site_url": "https://www.cyberciti.biz/",
        "feed_url": "https://www.cyberciti.biz/feed/",
        "category": "Linux: Sysadmin & Security",
        "best_for": "System administrators, DevOps workflows, shell tips, and security alerts.",
        "why_read": "Vivek Gite focuses on practical sysadmin work, containerization, server security vulnerabilities, and command-line tooling.",
        "enabled": 1
    },
    {
        "id": "linuxtoday",
        "name": "Linux Today",
        "site_url": "https://www.linuxtoday.com/",
        "feed_url": "https://www.linuxtoday.com/feed/",
        "category": "Linux: FOSS News Aggregation",
        "best_for": "Daily curated news aggregation across the entire FOSS world.",
        "why_read": "Acts as a central feed pulling together security advisories, enterprise open-source news, tutorials, and distro release notes.",
        "enabled": 1
    },
    {
        "id": "linuxuprising",
        "name": "Linux Uprising",
        "site_url": "https://www.linuxuprising.com/",
        "feed_url": "https://feeds.feedburner.com/LinuxUprising",
        "category": "Linux: Utilities & CLI",
        "best_for": "App reviews, small utility discovery, command-line tweaks, and PPA/Flatpak highlights.",
        "why_read": "Great for discovering niche open-source utilities, terminal tools, and detailed installation/configuration recipes.",
        "enabled": 1
    }
]

CURATED_GAMING_CATALOG = [
    {
        "id": "rockpapershotgun",
        "name": "Rock Paper Shotgun",
        "site_url": "https://www.rockpapershotgun.com/",
        "feed_url": "https://www.rockpapershotgun.com/feed",
        "category": "Gaming: PC & Indie",
        "best_for": "PC gaming, niche genres, simulation, strategy, and indie deep dives.",
        "why_read": "RPS focuses strictly on the PC ecosystem with sharp, voice-driven editorial work. Spotlights weird and wonderful indie gems, complex RPGs, and patch impressions.",
        "enabled": 1
    },
    {
        "id": "eurogamer",
        "name": "Eurogamer & Digital Foundry",
        "site_url": "https://www.eurogamer.net/",
        "feed_url": "https://www.eurogamer.net/feed",
        "category": "Gaming: Tech & Journalism",
        "best_for": "Rigorous journalism, in-depth reviews, and hardware performance breakdowns.",
        "why_read": "Respected European outlet for balanced critique and industry news. Digital Foundry is the gold standard for frame-rate analysis and graphics engine breakdowns.",
        "enabled": 1
    },
    {
        "id": "pcgamer",
        "name": "PC Gamer",
        "site_url": "https://www.pcgamer.com/",
        "feed_url": "https://www.pcgamer.com/rss/",
        "category": "Gaming: PC & Hardware",
        "best_for": "Mainstream PC gaming news, modding, hardware coverage, and major updates.",
        "why_read": "A long-running staple of PC gaming with fast reporting on major studio releases, hardware guides, patch breakdowns, and community mods.",
        "enabled": 1
    },
    {
        "id": "gamedeveloper",
        "name": "Game Developer",
        "site_url": "https://www.gamedeveloper.com/",
        "feed_url": "https://www.gamedeveloper.com/rss.xml",
        "category": "Gaming: Design & Engineering",
        "best_for": "Behind-the-scenes engineering, game design theory, and industry postmortems.",
        "why_read": "Written for and by creators, focusing on game engines, narrative design, rendering tech, AI mechanics, and developer realities.",
        "enabled": 1
    },
    {
        "id": "gamesindustry",
        "name": "GamesIndustry.biz",
        "site_url": "https://www.gamesindustry.biz/",
        "feed_url": "https://www.gamesindustry.biz/feed",
        "category": "Gaming: Industry & Business",
        "best_for": "The business, economics, mergers, sales data, and labor trends in gaming.",
        "why_read": "The definitive trade publication for tracking market shifts, developer acquisitions, platform revenues, and corporate decisions.",
        "enabled": 1
    },
    {
        "id": "aftermath",
        "name": "Aftermath",
        "site_url": "https://aftermath.site/",
        "feed_url": "https://aftermath.site/feed",
        "category": "Gaming: Independent Journalism",
        "best_for": "Independent games journalism, labor reporting, internet culture, and long-form essays.",
        "why_read": "Reader-supported, worker-owned cooperative founded by veteran games journalists. Free of corporate SEO incentives with investigative depth.",
        "enabled": 1
    },
    {
        "id": "nintendolife",
        "name": "Nintendo Life",
        "site_url": "https://www.nintendolife.com/",
        "feed_url": "https://www.nintendolife.com/feed",
        "category": "Gaming: Nintendo & Console",
        "best_for": "Dedicated coverage of Nintendo hardware, first-party releases, and eShop indies.",
        "why_read": "The premier hub for everything Nintendo, tracking hardware news, firmware updates, retro features, and exclusives.",
        "enabled": 1
    },
    {
        "id": "gematsu",
        "name": "Gematsu",
        "site_url": "https://www.gematsu.com/",
        "feed_url": "https://www.gematsu.com/feed",
        "category": "Gaming: Announcements & RPGs",
        "best_for": "Fast announcements, Japanese gaming news, RPGs, and release dates.",
        "why_read": "Direct, fast feed for press releases, development milestones, translation announcements, and overseas reveals without fluff.",
        "enabled": 1
    },
    {
        "id": "polygon",
        "name": "Polygon",
        "site_url": "https://www.polygon.com/",
        "feed_url": "https://www.polygon.com/rss/index.xml",
        "category": "Gaming: Features & Culture",
        "best_for": "Narrative deep dives, cultural commentary, guides, and long-form essays.",
        "why_read": "Balances mainstream release coverage with well-researched features examining game histories, artistic direction, and industry shifts.",
        "enabled": 1
    },
    {
        "id": "siliconera",
        "name": "Siliconera",
        "site_url": "https://www.siliconera.com/",
        "feed_url": "https://www.siliconera.com/feed/",
        "category": "Gaming: Japanese RPGs & Localization",
        "best_for": "International video game news, Japanese RPGs, localized indie releases, and developer interviews.",
        "why_read": "Reliable coverage on release dates, localization status, and overseas developer discussions that Western outlets often overlook.",
        "enabled": 1
    }
]

CURATED_LABOR_CATALOG = [
    {
        "id": "jacobin",
        "name": "Jacobin",
        "site_url": "https://jacobin.com/",
        "feed_url": "https://jacobin.com/feed",
        "category": "Politics: Democratic Socialism",
        "best_for": "Explicit democratic socialist political analysis, electoral commentary, and international history.",
        "why_read": "Flagship publication of the modern American democratic socialist movement, providing daily political commentary, historical essays, and ideological critique.",
        "enabled": 1
    },
    {
        "id": "inthesetimes",
        "name": "In These Times",
        "site_url": "https://inthesetimes.com/",
        "feed_url": "https://inthesetimes.com/rss",
        "category": "Politics: Labor & Organizing",
        "best_for": "Labor investigative reporting, workplace organizing, and grassroots social movements.",
        "why_read": "Founded in 1976 by socialist historian James Weinstein, dedicated to advancing economic justice, union campaigns, and working-class struggles.",
        "enabled": 1
    },
    {
        "id": "dissent",
        "name": "Dissent Magazine",
        "site_url": "https://www.dissentmagazine.org/",
        "feed_url": "https://www.dissentmagazine.org/feed/",
        "category": "Politics: Theory & Criticism",
        "best_for": "Long-form intellectual debate, democratic left theory, cultural criticism, and policy analysis.",
        "why_read": "Founded in 1954 by Irving Howe, featuring rigorous long-form debates on political strategy, foreign policy, and democratic theory.",
        "enabled": 1
    },
    {
        "id": "labornotes",
        "name": "Labor Notes",
        "site_url": "https://labornotes.org/",
        "feed_url": "https://labornotes.org/feed",
        "category": "Politics: Rank & File Unions",
        "best_for": "Rank-and-file union organizing, strike reporting, and workplace strategy.",
        "why_read": "Media and organizing project since 1979 reporting directly from shop floors, union halls, and contract fights across the US.",
        "enabled": 1
    },
    {
        "id": "thelever",
        "name": "The Lever",
        "site_url": "https://www.levernews.com/",
        "feed_url": "https://www.levernews.com/rss/",
        "category": "Politics: Investigative Journalism",
        "best_for": "Reader-supported investigative journalism on corporate lobbying, corruption, and money in politics.",
        "why_read": "Founded by David Sirota, investigating corporate malfeasance, campaign finance corruption, and regulatory capture with zero corporate advertising.",
        "enabled": 1
    },
    {
        "id": "democraticleft",
        "name": "Democratic Left (DSA)",
        "site_url": "https://www.dsausa.org/democratic-left/",
        "feed_url": "https://www.dsausa.org/feed/",
        "category": "Politics: Movement Strategy",
        "best_for": "Internal socialist strategy, local chapter organizing, and official movement analysis.",
        "why_read": "The official publication of the Democratic Socialists of America (DSA), offering coverage of local organizing drives and labor solidarity efforts.",
        "enabled": 1
    },
    {
        "id": "therealnews",
        "name": "The Real News Network (TRNN)",
        "site_url": "https://therealnews.com/",
        "feed_url": "https://therealnews.com/feed",
        "category": "Politics: Video & Audio Journalism",
        "best_for": "Video journalism, labor podcasts, racial and economic justice reporting.",
        "why_read": "Baltimore-based non-profit newsroom focusing on frontline worker interviews, police accountability, and grassroots labor actions.",
        "enabled": 1
    },
    {
        "id": "currentaffairs",
        "name": "Current Affairs",
        "site_url": "https://www.currentaffairs.org/",
        "feed_url": "https://currentaffairs.substack.com/feed",
        "category": "Politics: Essays & Media Criticism",
        "best_for": "Accessible political essays, media criticism, and witty socialist commentary.",
        "why_read": "Pairs colorful, readable design with rigorous breakdowns of neoliberal rhetoric, right-wing talking points, and mainstream media framing.",
        "enabled": 1
    },
    {
        "id": "dollarsandsense",
        "name": "Dollars & Sense",
        "site_url": "https://www.dollarsandsense.org/",
        "feed_url": "https://www.dollarsandsense.org/latest/rss/",
        "category": "Politics: Socialist Economics",
        "best_for": "Popular economic education and left analysis of fiscal/monetary policy.",
        "why_read": "Edited by economists and journalists since 1974, demystifying inflation, banking policy, corporate taxes, and trade agreements.",
        "enabled": 1
    },
    {
        "id": "dropsitenews",
        "name": "Drop Site News",
        "site_url": "https://www.dropsitenews.com/",
        "feed_url": "https://www.dropsitenews.com/feed",
        "category": "Politics: Foreign Policy & Whistleblowing",
        "best_for": "Investigative foreign policy, national security whistleblowing, and government transparency.",
        "why_read": "Founded by Ryan Grim and Jeremy Scahill, dedicated to unfiltered investigative reporting on US empire, defense contractors, and diplomacy.",
        "enabled": 1
    }
]

CURATED_CULTURE_CATALOG = [
    {
        "id": "vulture",
        "name": "Vulture (New York Magazine)",
        "site_url": "https://www.vulture.com/",
        "feed_url": "https://feeds.feedburner.com/nymag/vulture",
        "category": "Culture: Criticism & Pop Culture",
        "best_for": "Cultural criticism, television/film analysis, and smart pop culture journalism.",
        "why_read": "Treats modern entertainment with intellectual rigor and sharp humor, deconstructing modern media tropes and industry trends.",
        "enabled": 1
    },
    {
        "id": "pucknews",
        "name": "Puck News (What I'm Hearing)",
        "site_url": "https://puck.news/",
        "feed_url": "https://puck.news/feed/",
        "category": "Culture: Hollywood Business & Labor",
        "best_for": "Hard-nosed Hollywood business realities, executive infighting, and studio economics.",
        "why_read": "Matt Belloni skips press-junket fluff to focus on streaming deficits, executive churn, litigation, and behind-the-scenes labor struggles.",
        "enabled": 1
    },
    {
        "id": "theankler",
        "name": "The Ankler",
        "site_url": "https://theankler.com/",
        "feed_url": "https://theankler.com/feed",
        "category": "Culture: Industry Shakeups",
        "best_for": "Unvarnished Hollywood insider reporting, labor realities, and media shakeups.",
        "why_read": "Refuses to parrot studio PR, focusing on union negotiations, executive missteps, and entertainment industry shifts.",
        "enabled": 1
    },
    {
        "id": "defector",
        "name": "Defector",
        "site_url": "https://defector.com/",
        "feed_url": "https://defector.com/feed/",
        "category": "Culture: Worker-Owned Essays",
        "best_for": "Worker-owned cultural commentary, media critiques, and anti-corporate essays.",
        "why_read": "Subscriber-owned cooperative featuring sharp pop-culture essays, media ecosystem critiques, and zero access journalism.",
        "enabled": 1
    },
    {
        "id": "avclub",
        "name": "The A.V. Club",
        "site_url": "https://www.avclub.com/",
        "feed_url": "https://www.avclub.com/rss",
        "category": "Culture: Film & TV Reviews",
        "best_for": "Film and TV reviews, pop culture roundups, and media analysis.",
        "why_read": "Focuses on the art and cultural impact of film, television, and music rather than celebrity lifestyle coverage.",
        "enabled": 1
    },
    {
        "id": "popula",
        "name": "Popula",
        "site_url": "https://popula.com/",
        "feed_url": "https://popula.com/feed/",
        "category": "Culture: Alternative Essays",
        "best_for": "Alternative cultural essays, international perspectives, and media literacy.",
        "why_read": "Ad-free publication and Brick House cooperative member examining how wealth, power, and entertainment intersect in culture.",
        "enabled": 1
    },
    {
        "id": "indiewire",
        "name": "IndieWire",
        "site_url": "https://www.indiewire.com/",
        "feed_url": "https://www.indiewire.com/feed/",
        "category": "Culture: Indie Film & Craft",
        "best_for": "Independent filmmaking, festival circuits, and director/craft-focused reporting.",
        "why_read": "Prioritizes screenwriting, cinematography, and production mechanics over celebrity gossip and influencer lifestyles.",
        "enabled": 1
    },
    {
        "id": "thr_business",
        "name": "The Hollywood Reporter: Business & Labor",
        "site_url": "https://www.hollywoodreporter.com/c/business/",
        "feed_url": "https://www.hollywoodreporter.com/c/business/feed/",
        "category": "Culture: Labor & Guilds",
        "best_for": "Tracking strikes, union contracts (WGA, SAG-AFTRA, IATSE), and legal battles.",
        "why_read": "Essential reading on working conditions of below-the-line crews, guild negotiations, and entertainment anti-trust challenges.",
        "enabled": 1
    },
    {
        "id": "laineygossip",
        "name": "Lainey Gossip",
        "site_url": "https://www.laineygossip.com/",
        "feed_url": "https://www.laineygossip.com/rss",
        "category": "Culture: PR Deconstruction",
        "best_for": "Deconstructing celebrity PR strategies, media manipulation, and fame culture.",
        "why_read": "Approaches celebrity news to analyze the mechanics of Hollywood public relations, statements, and calculated media moves.",
        "enabled": 1
    },
    {
        "id": "nofilmschool",
        "name": "No Film School",
        "site_url": "https://nofilmschool.com/",
        "feed_url": "https://nofilmschool.com/rss.xml",
        "category": "Culture: Filmmaking & Crew Reality",
        "best_for": "Ground-level production reality, working-crew perspectives, and filmmaking economics.",
        "why_read": "Covers entertainment from the perspective of on-set crews, detailing market conditions and production realities without glamor.",
        "enabled": 1
    }
]

CURATED_SOURCES_CATALOG = CURATED_LINUX_CATALOG + CURATED_GAMING_CATALOG + CURATED_LABOR_CATALOG + CURATED_CULTURE_CATALOG

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
