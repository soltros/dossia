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
    
    # 2. Convert markdown links: [Label](url) -> Label (repeated for nested/adjacent)
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
    return re.sub(r'\s+', ' ', t).strip()

def _sentence_fingerprint(s: str) -> str:
    """Creates a normalized fingerprint for similarity matching and deduplication."""
    clean = re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    return clean[:40]

def extract_meaningful_sentences(text: str, seen_set: Set[str], max_count: int = 6) -> List[str]:
    """Extracts coherent, informative, non-repeating sentences from article text."""
    clean = strip_all_links_and_markdown(text)
    if not clean:
        return []
    
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    valid = []
    
    nav_phrases = [
        "skip to", "cookie", "privacy policy", "terms of", "all rights reserved",
        "subscribe", "sign in", "log in", "read more", "posted on", "written by",
        "click here", "share this", "leave a comment", "advertisement", "newsletter",
        "author guide", "events calendar", "affiliate link", "print recipe", "see policy",
        "jump to recipe", "save recipe", "recipe card", "similar articles", "departments",
        "departments politics", "view comments", "show full transcript"
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

def craft_editorial_narrative(category: str, primary_title: str, publishers: List[str], sentences: List[str]) -> str:
    """
    Crafts a warm, conversational, deeply journalistic 3-paragraph news story from source facts,
    giving the user comfortable editorial commentary rather than robotic snippets.
    """
    cat = (category or "").lower()
    pub_list = ", ".join(publishers) if publishers else "our monitored feeds"
    
    # Lead sentence
    s1 = sentences[0] if len(sentences) > 0 else f"A major conversation is unfolding around {primary_title}."
    s2 = sentences[1] if len(sentences) > 1 else "Covering journalists note key changes in policy, technical architecture, and community reception."
    s3 = sentences[2] if len(sentences) > 2 else ""
    s4 = sentences[3] if len(sentences) > 3 else ""

    # Paragraph 1: Conversational Hook & What Happened
    if "gaming" in cat or "game dev" in cat:
        para1 = f"There is notable movement in the gaming world this week, with reporting across {pub_list} focusing heavily on {primary_title}. {s1}"
    elif "labor" in cat or "politics" in cat:
        para1 = f"On the labor and political organizing front, reporting from {pub_list} highlights critical developments regarding {primary_title}. {s1}"
    elif "culture" in cat:
        para1 = f"In entertainment and cultural criticism, {pub_list} brings sharp analysis to {primary_title}. {s1}"
    elif "privacy" in cat or "security" in cat:
        para1 = f"Security researchers and privacy advocates are closely tracking {primary_title}, with detailed disclosures published across {pub_list}. {s1}"
    elif "ai" in cat or "machine learning" in cat:
        para1 = f"In the rapidly shifting local AI ecosystem, new engineering breakthroughs around {primary_title} are making waves across {pub_list}. {s1}"
    elif "food" in cat:
        para1 = f"For fermentation and baking enthusiasts, {pub_list} dives deep into the craft behind {primary_title}. {s1}"
    elif "music" in cat:
        para1 = f"Independent music circles are buzzing over {primary_title}, with new write-ups and reviews appearing across {pub_list}. {s1}"
    elif "linux" in cat or "hardware" in cat or "self-hosting" in cat:
        para1 = f"Systems engineers and open-source practitioners are digging into {primary_title}, as covered extensively by {pub_list}. {s1}"
    else:
        para1 = f"Across {pub_list}, significant attention is centering on {primary_title}. {s1}"

    # Paragraph 2: Substantive Technical Breakdown & Mechanics
    if s2 and s3:
        para2 = f"Looking at the specific mechanics, {s2} {s3}"
    elif s2:
        para2 = f"Diving into the practical details, {s2} {s4}".strip()
    else:
        para2 = "Maintainers and reporters emphasize the immediate architectural and workflow trade-offs at play."

    # Paragraph 3: Comfy Editorialization & Perspective
    if "gaming" in cat:
        para3 = "From an industry perspective, this underscores how quickly platform policies and player trust collide when studios make unilateral shifts. It's a reminder that community goodwill is hard-earned and easily strained."
    elif "labor" in cat:
        para3 = "These struggles reflect a broader momentum in rank-and-file organizing, where transparency and worker-led leverage continue to challenge entrenched management practices."
    elif "culture" in cat:
        para3 = "What makes this story compelling is how it cuts through standard PR talking points, exposing the underlying creative compromises and business pressures driving the modern entertainment machine."
    elif "food" in cat:
        para3 = "In the kitchen or bakery, small adjustments to microbial activity, flour composition, and temperature can completely transform the final crumb and flavor profile."
    elif "music" in cat:
        para3 = "In an era of hyper-algorithmic streaming playlists, independent releases like this prove that genuine DIY experimentation and organic community enthusiasm remain as vibrant as ever."
    elif "privacy" in cat or "security" in cat:
        para3 = "The broader takeaway here is the importance of defense-in-depth and auditing default permissions before minor configuration oversights turn into active exploits."
    elif "ai" in cat:
        para3 = "As open-weight models become more capable on consumer hardware, having transparent benchmarks and clean training provenance will be essential for developers building sustainable local workflows."
    elif "linux" in cat or "hardware" in cat or "self-hosting" in cat:
        para3 = "For engineers and self-hosters managing these systems, keeping dependencies tight and reviewing upstream changelogs ensures your stack remains resilient against unexpected breakage."
    else:
        para3 = "Ultimately, this is a development worth keeping on your radar as upstream teams continue to iterate and community feedback shapes the next release cycle."

    return f"{para1}\n\n{para2}\n\n{para3}"

async def generate_daily_dossier(edition_type: str = "morning", category: Optional[str] = "all") -> Dict[str, Any]:
    """
    Synthesizes the latest batch of articles into a rich, comfortable, human-written Intelligence Briefing
    with conversational storytelling, zero URL noise, and no robotic repetition.
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

    # Try LLM synthesis first if an LLM is connected (OpenAI, Anthropic, OpenRouter, Hermes)
    client = LLMClient()
    llm_dossier = None
    
    # Format clean context snippets for LLM
    article_snippets = []
    for a in clean_articles[:15]:
        snippet = (
            f"--- ARTICLE START ---\n"
            f"ID: {a['id']}\n"
            f"TITLE: {a['title']}\n"
            f"PUBLISHER: {a['publisher']}\n"
            f"CATEGORY: {a['category']}\n"
            f"CONTENT:\n{a['clean_body'][:1200]}\n"
            f"--- ARTICLE END ---"
        )
        article_snippets.append(snippet)
    
    articles_context_block = "\n\n".join(article_snippets)

    llm_prompt = f"""
You are the Chief Editorial Director and Host for Dossia's daily intelligence briefing titled "{category_title}".
Domain Focus: {selected_category}

Read the following source articles and write a cohesive, comfortable, deeply conversational intelligence briefing.
Tone: Warm, intelligent, conversational, insightful, and journalistic (like an expert podcast host or veteran columnist who genuinely read every piece and is breaking it down for the listener).
NEVER use generic corporate boilerplate (e.g. do not say "modular architectures and automated verification pipelines" for gaming, music, or labor news). Tailor your commentary directly to the human reality of {selected_category}.

SOURCE ARTICLES:
{articles_context_block}

RULES:
1. Executive TL;DR: 4 to 6 conversational, insightful bullet points summarizing the biggest stories in clear human language.
2. Story Capsules: Create 4 to 6 rich, multi-paragraph story capsules.
   - For each capsule, synthesize 2 to 3 related articles.
   - Write a rich 3-paragraph editorial narrative:
     * Paragraph 1: Conversational hook setting the stage, introducing the publications and key people.
     * Paragraph 2: Substantive breakdown of the exact facts, quotes, mechanisms, numbers, or arguments.
     * Paragraph 3: Warm, comfy editorial perspective on why this matters, community reaction, and future implications.
   - Key Takeaways: 3 to 4 punchy, substantive bullet points with specific facts, metrics, quotes, or actionable recommendations.
   - Reference the exact source article IDs in `source_article_ids`.

Output valid JSON matching this schema:
{{
  "title": "{category_title}",
  "executive_tldr": [
    "Conversational executive summary bullet 1...",
    "Conversational executive summary bullet 2..."
  ],
  "story_clusters": [
    {{
      "headline": "Engaging, Journalistic Headline",
      "category": "{selected_category}",
      "narrative_summary": "First paragraph hook...\\n\\nSecond paragraph breakdown...\\n\\nThird paragraph editorial perspective...",
      "key_takeaways": [
        "Publisher Name: Concrete takeaway detailing facts or findings...",
        "Publisher Name: Actionable insight or community reaction..."
      ],
      "signal_badge": "High Signal",
      "source_article_ids": ["id1", "id2"]
    }}
  ]
}}
"""
    messages = [
        {"role": "system", "content": "You are a master technical journalist and podcast host. Output ONLY valid JSON containing rich, conversational, comfy editorial prose with zero raw URLs or markdown clutter."},
        {"role": "user", "content": llm_prompt}
    ]

    try:
        response_text = await client.generate_chat_completion(messages, temperature=0.6, json_mode=True)
        if response_text:
            parsed = json.loads(response_text)
            if parsed.get("story_clusters") and len(parsed["story_clusters"]) >= 2:
                llm_dossier = parsed
                logger.info(f"Successfully generated LLM briefing for {selected_category}")
    except Exception as e:
        logger.warning(f"LLM briefing generation skipped or failed: {e}")

    # If LLM generation succeeded with rich story capsules, sanitize and use it
    if llm_dossier and llm_dossier.get("story_clusters"):
        exec_tldr = [strip_all_links_and_markdown(b) for b in llm_dossier.get("executive_tldr", [])]
        clusters_raw = []
        for c in llm_dossier.get("story_clusters", []):
            clusters_raw.append({
                "headline": strip_all_links_and_markdown(c["headline"]),
                "category": c.get("category", selected_category),
                "narrative_summary": strip_all_links_and_markdown(c["narrative_summary"]),
                "key_takeaways": [strip_all_links_and_markdown(t) for t in c.get("key_takeaways", [])],
                "signal_badge": c.get("signal_badge", "High Signal"),
                "source_article_ids": c.get("source_article_ids", [])
            })
    else:
        # High-craft Conversational Editorial Storytelling Engine
        logger.info(f"Synthesizing comfy editorial briefing for {selected_category} via storytelling engine.")
        seen_sentences: Set[str] = set()
        chunk_size = 3
        article_buckets = [clean_articles[i:i + chunk_size] for i in range(0, min(len(clean_articles), 18), chunk_size)]

        exec_tldr = []
        clusters_raw = []

        for idx, bucket in enumerate(article_buckets):
            primary = bucket[0]
            bucket_ids = [a["id"] for a in bucket]
            publishers = list(set(a["publisher"] for a in bucket))
            
            # Extract unique, informative sentences from across the bucket
            bucket_sentences = []
            for a in bucket:
                text_source = a["clean_body"] if len(a["clean_body"]) > 100 else a["clean_summary"]
                sents = extract_meaningful_sentences(text_source, seen_sentences, max_count=3)
                bucket_sentences.extend(sents)

            # Craft conversational narrative
            clean_t = primary['title']
            full_narrative = craft_editorial_narrative(selected_category, clean_t, publishers, bucket_sentences)

            # Clean headline with translation tag if applicable
            if clean_t.startswith('[Translated'):
                headline = clean_t
            elif primary.get("is_translated"):
                headline = f"[Translated from {primary['orig_lang']}] {clean_t}"
            else:
                headline = clean_t

            # Substantive, conversational Key Takeaways
            takeaways = []
            for a in bucket:
                t_sents = extract_meaningful_sentences(a["clean_body"] or a["clean_summary"], seen_sentences, max_count=1)
                t_text = t_sents[0] if t_sents else a["title"]
                t_text = strip_all_links_and_markdown(t_text)
                
                trans_note = f" (Translated from {a['orig_lang']})" if a.get("is_translated") else ""
                takeaways.append(f"{a['publisher']}{trans_note}: {t_text}")

            # Signal badge
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

            # High-level conversational executive bullet
            lead_fact = bucket_sentences[0] if bucket_sentences else clean_t
            exec_tldr.append(f"{primary['publisher']}: {clean_t} — {lead_fact[:150]}")

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
