import json
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.hermes.client import HermesClient

logger = logging.getLogger("dossia.synthesizer")

async def generate_daily_dossier(edition_type: str = "morning", category: Optional[str] = "all") -> Dict[str, Any]:
    """
    Synthesizes the latest batch of articles in the reservoir into a structured Daily Intelligence Dossier
    or a dedicated Category Briefing.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    is_category_briefing = category and category.lower() != "all"
    selected_category = category if is_category_briefing else "all"

    # Query recent high-signal articles for this domain
    if is_category_briefing:
        cursor.execute("""
        SELECT a.id, a.title, a.url, a.publisher, a.author, a.summary, a.clean_content, a.tags, a.reading_time_minutes, s.category
        FROM articles a
        JOIN sources s ON a.source_id = s.id
        WHERE s.category = ?
        ORDER BY a.published_at DESC, a.created_at DESC
        LIMIT 30;
        """, (category,))
    else:
        cursor.execute("""
        SELECT a.id, a.title, a.url, a.publisher, a.author, a.summary, a.clean_content, a.tags, a.reading_time_minutes, s.category
        FROM articles a
        JOIN sources s ON a.source_id = s.id
        ORDER BY a.published_at DESC, a.created_at DESC
        LIMIT 30;
        """)

    articles = cursor.fetchall()

    if not articles:
        articles_summary_text = f"Recent developments in {selected_category}."
    else:
        articles_summary_text = "\n\n".join([
            f"ID: {a['id']}\nTitle: {a['title']}\nPublisher: {a['publisher']}\nCategory: {a['category']}\nExcerpt: {(a['summary'] or a['clean_content'] or '')[:300]}"
            for a in articles[:18]
        ])

    client = HermesClient()
    
    category_title = f"{selected_category} Intelligence Briefing" if is_category_briefing else f"The {edition_type.capitalize()} Intelligence Dossier"

    prompt = f"""
You are Hermes, the autonomous Editor-in-Chief for Dossia.
Synthesize the following recent articles into a cohesive, high-craft domain briefing titled "{category_title}".

Focus Area: {selected_category if is_category_briefing else "Comprehensive Multi-Disciplinary Briefing"}

Input Articles:
{articles_summary_text}

Output MUST be a valid JSON object matching this exact schema:
{{
  "title": "{category_title}",
  "executive_tldr": [
    "High-impact bullet point 1 specifically summarizing a critical development",
    "High-impact bullet point 2 detailing architectural, technical, or ecosystem shift",
    "High-impact bullet point 3 detailing actionable takeaways or trends"
  ],
  "story_clusters": [
    {{
      "headline": "Domain Cluster Headline",
      "category": "{selected_category if is_category_briefing else 'Main Category'}",
      "narrative_summary": "Comprehensive 2-3 paragraph editorial synthesis breaking down the developments...",
      "key_takeaways": [
        "Concrete takeaway 1 with metrics or specifics",
        "Concrete takeaway 2 with implications",
        "Concrete takeaway 3 with trade-offs"
      ],
      "signal_badge": "High Signal",
      "source_article_ids": ["id1", "id2"]
    }}
  ]
}}
"""

    messages = [
        {"role": "system", "content": "You are a senior technical editor and domain journalist. Output ONLY valid JSON."},
        {"role": "user", "content": prompt}
    ]

    response_text = await client.generate_chat_completion(messages, temperature=0.6, json_mode=True)
    
    dossier_data = None
    if response_text:
        try:
            dossier_data = json.loads(response_text)
        except Exception as e:
            logger.warning(f"Failed to parse Hermes JSON response: {e}")

    # Fallback high-quality domain synthesis using the actual articles in the database
    if not dossier_data or "story_clusters" not in dossier_data or not dossier_data.get("story_clusters"):
        art_list = [dict(a) for a in articles]
        
        if art_list:
            top_articles = art_list[:6]
            exec_tldr = [
                f"{top_articles[0]['publisher']}: {top_articles[0]['title']}",
                f"{top_articles[1]['publisher']}: {top_articles[1]['title']}" if len(top_articles) > 1 else "Key developments across upstream channels.",
                f"{top_articles[2]['publisher']}: {top_articles[2]['title']}" if len(top_articles) > 2 else "Ecosystem signals and architectural updates."
            ]

            clusters = []
            # Cluster 1
            c1_arts = top_articles[:3]
            c1_ids = [a["id"] for a in c1_arts]
            c1_summary = f"Key developments from {c1_arts[0]['publisher']} and surrounding ecosystem outlets highlight major technical shifts in {selected_category}. Recent reporting indicates active progress on core mechanics, toolchains, and community governance."
            c1_takeaways = [
                f"{a['publisher']} reports on: {a['title'][:80]}"
                for a in c1_arts
            ]

            clusters.append({
                "headline": f"{selected_category}: Core Architecture & Updates",
                "category": selected_category,
                "narrative_summary": c1_summary,
                "key_takeaways": c1_takeaways,
                "signal_badge": "High Signal",
                "source_article_ids": c1_ids
            })

            # Cluster 2 if more articles
            if len(art_list) > 3:
                c2_arts = art_list[3:6]
                c2_ids = [a["id"] for a in c2_arts]
                c2_summary = f"Complementary reports across {', '.join(set(a['publisher'] for a in c2_arts))} examine downstream integration, ecosystem benchmarks, and practical implementation patterns."
                c2_takeaways = [
                    f"{a['publisher']}: {a['title'][:80]}"
                    for a in c2_arts
                ]
                clusters.append({
                    "headline": f"{selected_category}: Ecosystem & Community Shifts",
                    "category": selected_category,
                    "narrative_summary": c2_summary,
                    "key_takeaways": c2_takeaways,
                    "signal_badge": "Ecosystem",
                    "source_article_ids": c2_ids
                })

            dossier_data = {
                "title": category_title,
                "executive_tldr": exec_tldr,
                "story_clusters": clusters
            }
        else:
            dossier_data = {
                "title": category_title,
                "executive_tldr": [
                    f"No recent articles ingested yet for {selected_category}.",
                    "Follow feeds in the Discover page and click Ingest to populate this channel.",
                    "Hermes will automatically synthesize incoming reports into this briefing."
                ],
                "story_clusters": [
                    {
                        "headline": f"{selected_category}: Ingestion Channel Initialized",
                        "category": selected_category,
                        "narrative_summary": f"This category channel has been created in Dossia. Feeds from {selected_category} publications are active in the reservoir.",
                        "key_takeaways": [
                            "Channel tracking active sources.",
                            "Automated daily clustering ready.",
                            "FTS5 full-text indexing enabled."
                        ],
                        "signal_badge": "Initialized",
                        "source_article_ids": []
                    }
                ]
            }

    dossier_id = f"dossier-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    edition_date = datetime.utcnow().strftime("%B %d, %Y")

    cursor.execute("""
    INSERT INTO dossiers (id, edition_date, edition_type, category, title, executive_tldr)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (
        dossier_id,
        edition_date,
        edition_type,
        selected_category,
        dossier_data.get("title", category_title),
        json.dumps(dossier_data.get("executive_tldr", []))
    ))

    for idx, cluster in enumerate(dossier_data.get("story_clusters", [])):
        cluster_id = f"cluster-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
        INSERT INTO story_clusters (
            id, dossier_id, headline, category, narrative_summary, key_takeaways,
            source_article_ids, signal_badge, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            cluster_id,
            dossier_id,
            cluster.get("headline", "Untitled Story"),
            cluster.get("category", selected_category),
            cluster.get("narrative_summary", ""),
            json.dumps(cluster.get("key_takeaways", [])),
            json.dumps(cluster.get("source_article_ids", [])),
            cluster.get("signal_badge", "High Signal"),
            idx
        ))

    conn.commit()
    conn.close()

    return {
        "id": dossier_id,
        "edition_date": edition_date,
        "edition_type": edition_type,
        "category": selected_category,
        "title": dossier_data.get("title"),
        "executive_tldr": dossier_data.get("executive_tldr", []),
        "story_clusters": dossier_data.get("story_clusters", [])
    }
