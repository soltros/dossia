import re
import html
import json
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from backend.database import get_db_connection
from backend.hermes.client import LLMClient
from backend.ingest.translator import translate_to_english

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

def _sentence_fingerprint(s: str) -> str:
    """Creates a normalized fingerprint for similarity matching and deduplication."""
    clean = re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    return clean[:40]

def extract_unique_sentences(text: str, seen_set: Set[str], max_count: int = 4) -> List[str]:
    """Extracts coherent, informative, non-repeating sentences from article text."""
    clean = strip_all_links_and_markdown(text)
    if not clean:
        return []
    
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    valid = []
    
    nav_phrases = [
        "skip to", "cookie", "privacy policy", "terms of", "all rights reserved",
        "subscribe", "sign in", "log in", "read more", "posted on", "written by",
        "click here", "share this", "leave a comment", "advertisement", "newsletter"
    ]
    
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 35 or len(s_clean) > 350:
            continue
        if any(p in s_clean.lower() for p in nav_phrases):
            continue
        if not re.match(r'^[A-Z0-9"\'“‘]', s_clean):
            continue
            
        fp = _sentence_fingerprint(s_clean)
        if fp in seen_set:
            continue
            
        seen_set.add(fp)
        valid.append(s_clean)
        if len(valid) >= max_count:
            break
            
    return valid

def generate_domain_closing(category: str) -> str:
    """Generates a natural, domain-tailored closing analysis sentence."""
    cat = (category or "").lower()
    
    if "gaming" in cat or "game dev" in cat:
        return "For players, developers, and platform observers, these announcements reflect shifting ecosystem dynamics and creative release strategies across the current console and PC generation."
    elif "labor" in cat or "politics" in cat:
        return "These developments highlight ongoing rank-and-file campaigns, contract struggles, and institutional challenges shaping working-class politics and labor advocacy."
    elif "culture" in cat:
        return "Across modern entertainment and media, these shifting dynamics underscore evolving tensions between artistic independence, studio economics, and audience reception."
    elif "food" in cat or "fermentation" in cat:
        return "For bakers and culinary practitioners, mastering these biochemical mechanics, dough hydration curves, and fermentation rates ensures consistent, high-yield results."
    elif "music" in cat:
        return "These releases spotlight the creative vitality and sonic experimentation flourishing across independent DIY music communities."
    elif "privacy" in cat or "security" in cat:
        return "Security engineers and systems administrators should assess these vulnerability disclosures and audit existing access policies to mitigate potential attack surfaces."
    elif "ai" in cat or "machine learning" in cat:
        return "As open-weight models and local inference pipelines mature, these benchmarks provide essential guidance on architectural trade-offs, quantization limits, and memory efficiency."
    elif "hardware" in cat or "electronics" in cat:
        return "For embedded systems designers and hardware engineers, these boards and microcontrollers offer modular building blocks for rapid prototyping."
    elif "self-hosting" in cat or "homelab" in cat:
        return "For homelab operators and self-hosters, evaluating container isolation, network topologies, and storage resilience remains critical when deploying these services."
    else:
        return "These updates reflect active progress across the domain, offering actionable insights for practitioners tracking upstream technical and ecosystem changes."

async def generate_daily_dossier(edition_type: str = "morning", category: Optional[str] = "all") -> Dict[str, Any]:
    """
    Synthesizes the latest batch of articles into a clean, rich, human-readable Intelligence Briefing
    with ZERO raw URLs, NO repetition, and automatic English translation of foreign sources.
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

    # Clean and automatically translate foreign articles into English
    clean_articles = []
    for a in articles:
        raw_title = a["title"] or ""
        raw_body = a.get("clean_content") or a.get("summary") or ""
        raw_summary = a.get("summary") or ""
        
        # Translate title & body if in German or other foreign language
        trans_title, was_trans_title, lang_title = translate_to_english(raw_title)
        trans_body, was_trans_body, lang_body = translate_to_english(raw_body, max_chars=2000)
        
        is_translated = was_trans_title or was_trans_body
        orig_lang = lang_title if was_trans_title else lang_body

        clean_title = strip_all_links_and_markdown(trans_title)
        clean_body = strip_all_links_and_markdown(trans_body)
        clean_summary = strip_all_links_and_markdown(raw_summary)

        clean_articles.append({
            "id": a["id"],
            "title": clean_title or raw_title,
            "publisher": a["publisher"],
            "category": a.get("category") or selected_category,
            "clean_body": clean_body,
            "clean_summary": clean_summary,
            "url": a["url"],
            "is_translated": is_translated,
            "orig_lang": orig_lang
        })

    # Global sentence deduplication tracker across the entire briefing
    seen_sentences: Set[str] = set()

    # Group into thematic clusters of 2 to 3 articles each
    chunk_size = 3
    article_buckets = [clean_articles[i:i + chunk_size] for i in range(0, min(len(clean_articles), 18), chunk_size)]

    exec_tldr = []
    clusters_raw = []

    for idx, bucket in enumerate(article_buckets):
        primary = bucket[0]
        bucket_ids = [a["id"] for a in bucket]
        publishers = list(set(a["publisher"] for a in bucket))
        
        # Extract unique, non-repeating sentences from the bucket
        bucket_sentences = []
        for a in bucket:
            text_source = a["clean_body"] if len(a["clean_body"]) > 100 else a["clean_summary"]
            sents = extract_unique_sentences(text_source, seen_sentences, max_count=3)
            bucket_sentences.extend(sents)

        # Construct 3 non-repeating paragraphs
        if bucket_sentences:
            p1_lead = bucket_sentences[0]
            p2_detail = bucket_sentences[1] if len(bucket_sentences) > 1 else ""
            p2_context = bucket_sentences[2] if len(bucket_sentences) > 2 else ""
        else:
            p1_lead = f"Coverage from {primary['publisher']} focuses on core developments surrounding {primary['title']}."
            p2_detail = "Detailed reports outline the underlying context, implementation decisions, and community feedback."
            p2_context = ""

        # Clean headline with translation tag if applicable
        clean_t = primary['title']
        if clean_t.startswith('[Translated'):
            headline = clean_t
        elif primary.get("is_translated"):
            headline = f"[Translated from {primary['orig_lang']}] {clean_t}"
        else:
            headline = clean_t

        para1 = f"Recent reporting from {', '.join(publishers)} highlights key developments regarding {clean_t}. {p1_lead}"
        para2 = f"{p2_detail} {p2_context}".strip()
        para3 = generate_domain_closing(selected_category)

        full_narrative = f"{para1}\n\n{para2}\n\n{para3}"

        # Clean, unique Key Takeaways (NO repetition of paragraph 1 or 2)
        takeaways = []
        for a in bucket:
            # Extract a distinct takeaway sentence
            t_sents = extract_unique_sentences(a["clean_body"] or a["clean_summary"], seen_sentences, max_count=1)
            t_text = t_sents[0] if t_sents else a["title"]
            t_text = strip_all_links_and_markdown(t_text)
            
            trans_note = f" (Translated from {a['orig_lang']})" if a.get("is_translated") else ""
            takeaways.append(f"{a['publisher']}{trans_note}: {t_text}")

        # Determine signal badge
        badge = "High Signal"
        if primary.get("is_translated"):
            badge = f"Translated ({primary['orig_lang']})"
        else:
            lower_t = primary["title"].lower()
            if any(w in lower_t for w in ["security", "vulnerability", "cve", "patch", "exploit", "breach"]):
                badge = "Security Alert"
            elif any(w in lower_t for w in ["benchmark", "performance", "speed", "test"]):
                badge = "Benchmark"
            elif any(w in lower_t for w in ["release", "launch", "announces", "debut"]):
                badge = "Release"
            elif any(w in lower_t for w in ["interview", "deep dive", "analysis", "review"]):
                badge = "Analysis"

        clusters_raw.append({
            "headline": headline,
            "category": primary["category"],
            "narrative_summary": full_narrative,
            "key_takeaways": takeaways,
            "signal_badge": badge,
            "source_article_ids": bucket_ids
        })

        # Distinct high-level summary for Executive TL;DR
        exec_tldr.append(f"{primary['publisher']}: {headline} — {p1_lead[:160]}")

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
