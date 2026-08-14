import re
import json
import logging
from typing import Dict, Any, List
from backend.hermes.client import LLMClient

logger = logging.getLogger("dossia.podcast.script")

def _clean_tts_text(text: str) -> str:
    if not text:
        return ""
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'#+\s*', '', t)
    t = re.sub(r'[`_~]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

async def generate_podcast_script_with_chapters(dossier: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a synthesized Dossier and generates a comprehensive, broadcast-quality spoken podcast script
    with dynamic chapter timestamps based on the actual story clusters.
    """
    client = LLMClient()
    
    title = dossier.get("title", "Daily Technical Intelligence")
    edition_date = dossier.get("edition_date", "Today")
    category = dossier.get("category", "Technology")
    exec_bullets = dossier.get("executive_tldr", [])
    clusters = dossier.get("story_clusters", [])

    clusters_formatted_text = ""
    for idx, c in enumerate(clusters):
        takeaways_str = " ".join([_clean_tts_text(t) for t in c.get("key_takeaways", [])])
        clusters_formatted_text += (
            f"\n\n--- STORY CAPSULE {idx+1}: {c.get('headline')} ({c.get('category')}) ---\n"
            f"Narrative:\n{_clean_tts_text(c.get('narrative_summary', ''))}\n"
            f"Key Points:\n{takeaways_str}\n"
        )

    prompt = f"""
You are the host and senior technical editor of the Dossia Intelligence Audio Briefing.
Write a comprehensive, broadcast-ready 5 to 7 minute spoken audio script for today's briefing.

Briefing Details:
Title: {title}
Edition Date: {edition_date}
Category Domain: {category}

Executive Highlights:
{chr(10).join(['- ' + _clean_tts_text(b) for b in exec_bullets])}

Deep Dive Stories:
{clusters_formatted_text}

INSTRUCTIONS:
1. Speak in a natural, authoritative, crisp editorial tone (like a senior BBC or NPR technology editor).
2. Cover the Executive Highlights first, then systematically break down EACH story capsule with its technical mechanics, benchmarks, and architectural takeaways.
3. Output MUST be valid JSON with chapter marks accurately estimating time offsets.

Output JSON format:
{{
  "episode_title": "{title} - {edition_date}",
  "full_transcript": "Spoken script covering intro, executive overview, and all story capsules...",
  "chapters": [
    {{"title": "Introduction & Executive Overview", "start_seconds": 0}},
    {{"title": "Chapter 1 Title", "start_seconds": 60}},
    {{"title": "Chapter 2 Title", "start_seconds": 180}},
    {{"title": "Editorial Wrap & Takeaways", "start_seconds": 320}}
  ],
  "duration_seconds": 360
}}
"""

    messages = [
        {"role": "system", "content": "You are a professional broadcast podcast writer. Output ONLY valid JSON."},
        {"role": "user", "content": prompt}
    ]

    response_text = await client.generate_chat_completion(messages, temperature=0.6, json_mode=True)
    if response_text:
        try:
            parsed = json.loads(response_text)
            if parsed.get("full_transcript") and len(parsed["full_transcript"]) > 200:
                return parsed
        except Exception as e:
            logger.warning(f"Error parsing podcast script JSON: {e}")

    # Dynamic local broadcast script generation directly from actual cluster content
    logger.info("Building dynamic full-length broadcast script from dossier clusters.")
    script_segments = []
    chapters = []
    current_time_sec = 0

    # Intro segment
    intro = (
        f"Welcome to the Dossia {title} for {edition_date}. "
        f"I'm your autonomous editorial intelligence host. "
        f"Here is your executive briefing covering the latest high-signal developments.\n\n"
    )
    for b in exec_bullets:
        clean_b = _clean_tts_text(b)
        intro += f"First: {clean_b}. "
    
    script_segments.append(intro)
    chapters.append({"title": "Introduction & Executive Overview", "start_seconds": 0})
    # Estimate ~140 words per minute (2.3 words/sec)
    current_time_sec += max(45, int(len(intro.split()) / 2.3))

    # Iterate through all story capsules
    for idx, c in enumerate(clusters):
        headline = c.get("headline", f"Story {idx+1}")
        narrative = _clean_tts_text(c.get("narrative_summary", ""))
        takeaways = [_clean_tts_text(t) for t in c.get("key_takeaways", [])]

        story_text = f"\n\nStory number {idx+1}: {headline}.\n\n{narrative}\n\n"
        if takeaways:
            story_text += "Here are the key technical takeaways from this reporting: "
            for t in takeaways:
                story_text += f"{t}. "

        chapters.append({"title": headline[:45], "start_seconds": current_time_sec})
        script_segments.append(story_text)
        current_time_sec += max(60, int(len(story_text.split()) / 2.3))

    # Outro segment
    outro = (
        f"\n\nThat concludes today's {title}. "
        f"You can explore full-text article sources, run interactive margin queries, and subscribe via Podcasting 2.0 on your Dossia dashboard. "
        f"Thank you for listening, and have a productive day."
    )
    chapters.append({"title": "Editorial Wrap & Outro", "start_seconds": current_time_sec})
    script_segments.append(outro)
    current_time_sec += 25

    full_script = "".join(script_segments)

    return {
        "episode_title": f"Dossia Briefing: {title}",
        "full_transcript": full_script,
        "chapters": chapters,
        "duration_seconds": current_time_sec
    }
