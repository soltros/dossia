import json
import logging
from datetime import datetime
from email.utils import format_datetime
from typing import List, Dict, Any
from backend.config import settings
from backend.database import get_db_connection

logger = logging.getLogger("dossia.podcast.rss")

def generate_podcast_rss_xml(base_url: str) -> str:
    """
    Generates a fully compliant Podcasting 2.0 RSS XML feed with chapters and transcripts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, dossier_id, episode_number, title, description, audio_url, duration_seconds, chapters, transcript, published_at
    FROM podcast_episodes
    ORDER BY episode_number DESC;
    """)
    episodes = cursor.fetchall()
    conn.close()

    items_xml = []
    for ep in episodes:
        audio_full_url = ep["audio_url"] if ep["audio_url"].startswith("http") else f"{base_url.rstrip('/')}{ep['audio_url']}"
        chapters_url = f"{base_url.rstrip('/')}/api/episodes/{ep['id']}/chapters.json"
        transcript_url = f"{base_url.rstrip('/')}/api/episodes/{ep['id']}/transcript.txt"
        
        try:
            pub_date = datetime.fromisoformat(ep["published_at"])
            pub_date_rfc = format_datetime(pub_date)
        except Exception:
            pub_date_rfc = format_datetime(datetime.utcnow())

        item = f"""
    <item>
      <title><![CDATA[{ep['title']}]]></title>
      <link>{base_url}</link>
      <guid isPermaLink="false">dossia-ep-{ep['id']}</guid>
      <pubDate>{pub_date_rfc}</pubDate>
      <description><![CDATA[{ep['description']}]]></description>
      <enclosure url="{audio_full_url}" length="2048000" type="audio/mpeg" />
      <itunes:duration>{ep['duration_seconds']}</itunes:duration>
      <itunes:episode>{ep['episode_number']}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <podcast:chapters url="{chapters_url}" type="application/json" />
      <podcast:transcript url="{transcript_url}" type="text/plain" />
    </item>"""
        items_xml.append(item)

    now_rfc = format_datetime(datetime.utcnow())
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:podcast="https://podcastindex.org/namespace/1.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title><![CDATA[{settings.podcast_title}]]></title>
    <link>{base_url}</link>
    <language>en-us</language>
    <copyright>Dossia &amp; Soltros</copyright>
    <itunes:author>{settings.podcast_author}</itunes:author>
    <itunes:summary><![CDATA[{settings.podcast_description}]]></itunes:summary>
    <description><![CDATA[{settings.podcast_description}]]></description>
    <itunes:owner>
      <itunes:name>{settings.podcast_author}</itunes:name>
      <itunes:email>podcast@dossia.local</itunes:email>
    </itunes:owner>
    <itunes:image href="{base_url.rstrip('/')}/static/icons/podcast-cover.png" />
    <itunes:category text="Technology">
      <itunes:category text="Tech News" />
    </itunes:category>
    <lastBuildDate>{now_rfc}</lastBuildDate>
    <podcast:locked>no</podcast:locked>
    <podcast:guid>dossia-daily-intelligence-feed</podcast:guid>
    {''.join(items_xml)}
  </channel>
</rss>"""
    return xml
