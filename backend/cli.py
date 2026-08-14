"""
Dossia Command-Line Interface (CLI) & Editorial Synthesis Hook
Run directly via: python -m backend.cli <command> [args]
"""

import sys
import json
import asyncio
import argparse
from typing import Optional
from backend.config import settings
from backend.database import init_db, get_db_connection
from backend.hermes.synthesizer import generate_daily_dossier
from backend.ingest.rss import run_all_ingestions
from backend.podcast.tts_engine import TTSEngine

def cmd_init():
    """Initializes the database and seeds the curated catalog."""
    print("Initializing Dossia database...")
    init_db()
    print("Dossia database initialized.")

def cmd_ingest():
    """Runs RSS ingestion across all active sources."""
    print("Starting feed ingestion across all enabled channels...")
    res = asyncio.run(run_all_ingestions())
    print(f"Ingestion complete: {res.get('total_new_articles', 0)} new articles added across {res.get('sources_processed', 0)} sources.")

def cmd_synthesize(category: Optional[str] = "all", provider: Optional[str] = None, format_type: str = "text"):
    """
    Synthesizes an Intelligence Briefing for a specific category (or master all-in-one).
    Can be used by the assistant or user in terminal.
    """
    if provider:
        settings.llm_provider = provider

    cat_label = category if category and category.lower() != "all" else "All Intelligence"
    print(f"Synthesizing Dossia Briefing for [{cat_label}] using LLM provider: {settings.llm_provider}...")
    
    dossier = asyncio.run(generate_daily_dossier(edition_type="morning", category=category or "all"))

    if format_type == "json":
        print(json.dumps(dossier, indent=2))
        return

    print("\n" + "=" * 70)
    print(f"  {dossier['title'].upper()}")
    print(f"  Edition: {dossier.get('edition_type', 'Daily').capitalize()} • {dossier.get('edition_date', 'Today')}")
    print("=" * 70 + "\n")

    print("EXECUTIVE 60-SECOND BRIEFING:")
    for bullet in dossier.get("executive_tldr", []):
        print(f"  • {bullet}")
    print()

    print("STORY CLUSTERS:")
    for cluster in dossier.get("story_clusters", []):
        print("-" * 70)
        print(f"[{cluster.get('category', cat_label)}] {cluster.get('headline')}")
        print(f"Signal: {cluster.get('signal_badge', 'High Signal')}")
        print()
        print(cluster.get("narrative_summary", ""))
        print("\nKey Takeaways:")
        for t in cluster.get("key_takeaways", []):
            print(f"  - {t}")
        print()

def cmd_search(query: str, limit: int = 10):
    """Full-text FTS5 search across the reservoir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id, a.title, a.publisher, a.url, a.published_at, s.category
    FROM articles_fts f
    JOIN articles a ON f.id = a.id
    JOIN sources s ON a.source_id = s.id
    WHERE articles_fts MATCH ?
    ORDER BY rank
    LIMIT ?;
    """, (query, limit))
    rows = cursor.fetchall()
    conn.close()

    print(f"Search results for query '{query}' ({len(rows)} matches):")
    for r in rows:
        print(f" • [{r['category']}] {r['publisher']}: {r['title']} ({r['url']})")

def main():
    parser = argparse.ArgumentParser(description="Dossia CLI - Autonomous Editorial & Knowledge Hub")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # init
    subparsers.add_parser("init", help="Initialize and migrate database")

    # ingest
    subparsers.add_parser("ingest", help="Ingest feeds across all followed publications")

    # synthesize
    synth_parser = subparsers.add_parser("synthesize", help="Synthesize daily dossier or category briefing")
    synth_parser.add_argument("--category", "-c", default="all", help="Domain category (e.g. 'Linux & Kernel', 'Local AI & Machine Learning')")
    synth_parser.add_argument("--provider", "-p", default=None, help="LLM Provider override ('openai', 'anthropic', 'openrouter', 'hermes')")
    synth_parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")

    # search
    search_parser = subparsers.add_parser("search", help="Search reservoir with FTS5")
    search_parser.add_argument("query", help="Search terms")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum results")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "ingest":
        cmd_ingest()
    elif args.command == "synthesize":
        cmd_synthesize(category=args.category, provider=args.provider, format_type=args.format)
    elif args.command == "search":
        cmd_search(query=args.query, limit=args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
