import re
import html
import json
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.hermes.client import LLMClient

logger = logging.getLogger("dossia.synthesizer")

def strip_all_links_and_markdown(text: str) -> str:
    """
    Absolute Reader Mode prose sanitizer:
    Converts '[Link Text](https://...)' to just 'Link Text'.
    Strips all raw URLs (https://..., www....), isolated paths, markdown symbols, and bracket junk.
    """
    if not text:
        return ""
    
    t = html.unescape(text)
    
    # 1. Strip images: ![alt](url) -> ''
    t = re.sub(r'!\[.*?\]\(.*?\)', '', t)
    
    # 2. Convert markdown links: [Label](url) -> Label (do this repeatedly for nested/adjacent)
    t = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', t)
    
    # 3. Strip all raw URLs, protocols, query strings
    t = re.sub(r'https?://\S+', '', t)
    t = re.sub(r'www\.\S+', '', t)
    t = re.sub(r'mailto:\S+', '', t)
    
    # 4. Strip isolated URL paths (/foo/bar), file extensions
    t = re.sub(r'\(\/[^\)]+\)', '', t)
    t = re.sub(r'\/[A-Za-z0-9_\-\.\/]{3,}', '', t)
    t = re.sub(r'\.(php|html|htm|xml|json|rss|atom|asp|aspx|jsp)', '', t, flags=re.IGNORECASE)
    
    # 5. Strip isolated brackets like [1], [2], [$], [#], [LWN.net], [More info]
    t = re.sub(r'\[\s*[\d\$#\*\-]+\s*\]', '', t)
    t = re.sub(r'\[\s*\]', '', t)
    t = re.sub(r'\[[A-Za-z0-9\.\-_ /]{1,30}\]', '', t)
    
    # 6. Strip markdown symbols (#, *, _, `, ~, |, >, \)
    t = re.sub(r'[`*~_#|<>\/\\\^=+%\$]', ' ', t)
    t = re.sub(r'[{}\[\]\(\)]', ' ', t)
    t = re.sub(r'—|–|--+', ' — ', t)
    
    # 7. Normalize whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_meaningful_sentences(text: str, max_count: int = 3) -> List[str]:
    """Extracts coherent, informative sentences from article text."""
    clean = strip_all_links_and_markdown(text)
    if not clean:
        return []
    
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    valid = []
    
    # Filter out navigation phrases and short fragments
    nav_phrases = [
        "skip to", "cookie", "privacy policy", "terms of", "all rights reserved",
        "subscribe", "sign in", "log in", "read more", "posted on", "written by",
        "click here", "share this", "leave a comment", "advertisement"
    ]
    
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 35 or len(s_clean) > 350:
            continue
        if any(p in s_clean.lower() for p in nav_phrases):
            continue
        if re.match(r'^[A-Z0-9"\'“‘]', s_clean):
            valid.append(s_clean)
            
    return valid[:max_count]

def generate_domain_closing(category: str, topic: str) -> str:
    """Generates a natural, domain-tailored closing analysis sentence."""
    cat = (category or "").lower()
    
    if "gaming" in cat or "game dev" in cat:
        return f"For players, developers, and industry observers, these announcements signal shifting platform dynamics and creative strategies across the current generation."
    elif "labor" in cat or "politics" in cat:
        return f"These developments reflect broader organizing trends and institutional challenges facing working-class communities and labor unions nationwide."
    elif "culture" in cat:
        return f"Across modern media and entertainment, these shifting dynamics highlight ongoing debates around artistic independence, platform control, and audience engagement."
    elif "food" in cat or "fermentation" in cat:
        return f"For bakers and fermentation practitioners, understanding these precise biochemical interactions and hydration dynamics is key to achieving consistent, high-quality results."
    elif "music" in cat:
        return f"These releases highlight the creative vitality of independent music scenes operating outside mainstream commercial algorithms."
    elif "privacy" in cat or "security" in cat:
        return f"Security practitioners and systems engineers should evaluate these threat vectors and audit relevant configurations across active infrastructure."
    elif "ai" in cat or "machine learning" in cat:
        return f"As open models and local inference toolchains evolve, these benchmarks provide valuable insights into resource allocation and model capabilities."
    elif "hardware" in cat or "electronics" in cat:
        return f"For makers and embedded hardware designers, these boards and components offer flexible options for low-power edge prototyping."
    else:
        return f"These updates reflect active progress across the ecosystem, offering valuable insights for engineers and practitioners tracking upstream developments."

async def generate_daily_dossier(edition_type: str = "morning", category: Optional[str] = "all") -> Dict[str, Any]:
    """
    Synthesizes the latest batch of articles into a clean, rich, human-readable Intelligence Briefing
    with ZERO raw URLs, bracket clutter, or robotic boilerplate.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    is_category_briefing = category and category.lower() != "all"
    selected_category = category if is_category_briefing else "all"

    # Query up to 35 most recent articles
    if is_category_briefing:
        cursor.execute("""
        SELECT a.id, a.title, a.url, a.publisher, a.author, a.summary, a.clean_content, a.tags, a.reading_time_minutes, a.published_at, s.category
        FROM articles a
        JOIN sources s ON a.source_id = s.id
        WHERE s.category = ?
        ORDER BY a.published_at DESC, a.created_at DESC
        LIMIT 35;
        """, (category,))
    else:
        cursor.execute("""
        SELECT a.id, a.title, a.url, a.publisher, a.author, a.summary, a.clean_content, a.tags, a.reading_time_minutes, a.published_at, s.category
        FROM articles a
        JOIN sources s ON a.source_id = s.id
        ORDER BY a.published_at DESC, a.created_at DESC
        LIMIT 35;
        """)

    articles = [dict(a) for a in cursor.fetchall()]
    category_title = f"{selected_category} Intelligence Briefing" if is_category_briefing else f"The {edition_type.capitalize()} Intelligence Dossier"

    if not articles:
        return {
            "id": f"dossier-empty-{uuid.uuid4().hex[:6]}",
            "edition_date": datetime.now().strftime("%B %d, %Y"),
            "edition_type": edition_type,
            "category": selected_category,
            "title": category_title,
            "executive_tldr": [
                f"No articles indexed yet for {selected_category}.",
                "Follow publications in the Discover tab and click Ingest to fetch live feeds."
            ],
            "story_clusters": []
        }

    # Clean all article content
    clean_articles = []
    for a in articles:
        clean_title = strip_all_links_and_markdown(a["title"])
        clean_body = strip_all_links_and_markdown(a.get("clean_content") or a.get("summary") or "")
        clean_summary = strip_all_links_and_markdown(a.get("summary") or "")
        clean_articles.append({
            "id": a["id"],
            "title": clean_title or a["title"],
            "publisher": a["publisher"],
            "category": a.get("category") or selected_category,
            "clean_body": clean_body,
            "clean_summary": clean_summary,
            "url": a["url"]
        })

    # Group into thematic clusters of 2 to 3 articles each
    chunk_size = 3
    article_buckets = [clean_articles[i:i + chunk_size] for i in range(0, min(len(clean_articles), 18), chunk_size)]

    exec_tldr = []
    clusters_raw = []

    for idx, bucket in enumerate(article_buckets):
        primary = bucket[0]
        bucket_ids = [a["id"] for a in bucket]
        publishers = list(set(a["publisher"] for a in bucket))
        
        # Extract real body sentences from bucket articles
        all_sentences = []
        for a in bucket:
            sents = extract_meaningful_sentences(a["clean_body"] or a["clean_summary"], 3)
            all_sentences.extend(sents)

        # Build clean narrative paragraphs
        p1_lead = all_sentences[0] if len(all_sentences) > 0 else f"Recent reporting from {primary['publisher']} covers key developments regarding {primary['title']}."
        p2_detail = all_sentences[1] if len(all_sentences) > 1 else (all_sentences[0] if all_sentences else "Coverage details key announcements, structural context, and direct user feedback.")
        p2_context = all_sentences[2] if len(all_sentences) > 2 else ""
        p3_closing = generate_domain_closing(selected_category, primary['title'])

        para1 = f"Recent reporting from {', '.join(publishers)} highlights significant developments regarding {primary['title']}. {p1_lead}"
        para2 = f"{p2_detail} {p2_context}".strip()
        para3 = p3_closing

        full_narrative = f"{para1}\n\n{para2}\n\n{para3}"

        # Clean, natural Key Takeaways (NO empty labels or dangling colons)
        takeaways = []
        for a in bucket:
            sents = extract_meaningful_sentences(a["clean_body"] or a["clean_summary"], 1)
            takeaway_text = sents[0] if sents else a["title"]
            takeaway_text = strip_all_links_and_markdown(takeaway_text)
            takeaways.append(f"{a['publisher']}: {takeaway_text}")

        # Add a specific context takeaway if additional sentences exist
        if len(all_sentences) > 3:
            takeaways.append(f"Key Detail: {strip_all_links_and_markdown(all_sentences[3])}")

        # Determine signal badge
        badge = "High Signal"
        lower_t = primary["title"].lower()
        if any(w in lower_t for w in ["security", "vulnerability", "cve", "patch", "exploit", "breach"]):
            badge = "Security Alert"
        elif any(w in lower_t for w in ["benchmark", "performance", "speed", "test"]):
            badge = "Benchmark"
        elif any(w in lower_t for w in ["release", "launch", "announces", "debut"]):
            badge = "Release"
        elif any(w in lower_t for w in ["interview", "deep dive", "analysis", "review"]):
            badge = "Analysis"

        headline = strip_all_links_and_markdown(primary["title"])

        clusters_raw.append({
            "headline": headline,
            "category": primary["category"],
            "narrative_summary": full_narrative,
            "key_takeaways": takeaways,
            "signal_badge": badge,
            "source_article_ids": bucket_ids
        })

        # Add clean bullet to Executive TL;DR
        lead_summary = all_sentences[0] if all_sentences else primary["title"]
        exec_tldr.append(f"{primary['publisher']}: {headline} — {lead_summary}")

    # Limit executive TLDR to top 6 points
    exec_tldr = exec_tldr[:6]

    # Save generated dossier into SQLite
    dossier_id = f"dossier-{datetime.now().strftime('%Y%m%d')}-{selected_category.lower().replace(' ', '-').replace('&', 'and')}-{uuid.uuid4().hex[:4]}"
    today_str = datetime.now().strftime("%B %d, %Y")

    cursor.execute("""
    INSERT INTO dossiers (id, edition_date, edition_type, category, title, executive_tldr)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (
        dossier_id,
        today_str,
        edition_type,
        selected_category,
        category_title,
        json.dumps(exec_tldr)
    ))

    # Save story clusters
    for idx, c in enumerate(clusters_raw):
        cluster_id = f"cluster-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO story_clusters (
            id, dossier_id, headline, category, narrative_summary,
            key_takeaways, source_article_ids, signal_badge, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            cluster_id,
            dossier_id,
            c["headline"],
            c.get("category", selected_category),
            c["narrative_summary"],
            json.dumps(c.get("key_takeaways", [])),
            json.dumps(c.get("source_article_ids", [])),
            c.get("signal_badge", "High Signal"),
            idx
        ))

    conn.commit()

    # Re-fetch populated dossier with source article objects
    cursor.execute("SELECT * FROM dossiers WHERE id = ?", (dossier_id,))
    dossier_row = dict(cursor.fetchone())
    dossier_row["executive_tldr"] = json.loads(dossier_row["executive_tldr"])

    cursor.execute("SELECT * FROM story_clusters WHERE dossier_id = ? ORDER BY sort_order ASC;", (dossier_id,))
    story_clusters = []
    for r in cursor.fetchall():
        cluster_item = dict(r)
        cluster_item["key_takeaways"] = json.loads(cluster_item["key_takeaways"]) if cluster_item.get("key_takeaways") else []
        src_ids = json.loads(cluster_item["source_article_ids"]) if cluster_item.get("source_article_ids") else []
        
        sources = []
        if src_ids:
            placeholders = ",".join("?" for _ in src_ids)
            cursor.execute(f"SELECT id, title, publisher, url FROM articles WHERE id IN ({placeholders});", src_ids)
            sources = [dict(sr) for sr in cursor.fetchall()]
        
        cluster_item["sources"] = sources
        story_clusters.append(cluster_item)

    dossier_row["story_clusters"] = story_clusters
    conn.close()

    return dossier_row
