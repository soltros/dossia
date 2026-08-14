import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Response
from typing import List, Dict, Any, Optional
from backend.database import get_db_connection
from backend.config import settings
from backend.podcast.rss_builder import generate_podcast_rss_xml
from backend.podcast.script_writer import generate_podcast_script_with_chapters
from backend.podcast.tts_engine import TTSEngine

router = APIRouter(tags=["podcast"])

@router.get("/podcast.xml")
@router.get("/api/podcast.xml")
async def get_podcast_xml(request: Request):
    base_url = str(request.base_url)
    xml_content = generate_podcast_rss_xml(base_url)
    return Response(content=xml_content, media_type="application/xml")

@router.get("/api/episodes")
async def list_episodes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, dossier_id, episode_number, title, description, audio_url, duration_seconds, chapters, transcript, published_at
    FROM podcast_episodes
    ORDER BY episode_number DESC;
    """)
    rows = cursor.fetchall()
    conn.close()

    episodes = []
    for r in rows:
        ep = dict(r)
        ep["chapters"] = json.loads(ep["chapters"]) if ep.get("chapters") else []
        episodes.append(ep)
    return episodes

@router.get("/api/episodes/{episode_id}/chapters.json")
async def get_episode_chapters(episode_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chapters FROM podcast_episodes WHERE id = ?", (episode_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Episode not found")

    chapters = json.loads(row["chapters"]) if row["chapters"] else []
    return {
        "version": "1.2.0",
        "chapters": [
            {"startTime": c["start_seconds"], "title": c["title"]} for c in chapters
        ]
    }

@router.get("/api/episodes/{episode_id}/transcript.txt")
async def get_episode_transcript(episode_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT transcript FROM podcast_episodes WHERE id = ?", (episode_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row["transcript"]:
        raise HTTPException(status_code=404, detail="Transcript not found")

    return Response(content=row["transcript"], media_type="text/plain")

@router.post("/api/episodes/generate")
async def generate_episode_from_latest_dossier():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get latest dossier
    cursor.execute("""
    SELECT id, edition_date, edition_type, title, executive_tldr
    FROM dossiers
    ORDER BY created_at DESC
    LIMIT 1;
    """)
    dossier_row = cursor.fetchone()
    if not dossier_row:
        conn.close()
        raise HTTPException(status_code=400, detail="No dossier found to convert into a podcast.")

    dossier = dict(dossier_row)
    dossier["executive_tldr"] = json.loads(dossier["executive_tldr"])

    # Fetch clusters
    cursor.execute("""
    SELECT headline, category, narrative_summary, key_takeaways
    FROM story_clusters
    WHERE dossier_id = ?
    ORDER BY sort_order ASC;
    """, (dossier["id"],))
    dossier["story_clusters"] = [dict(r) for r in cursor.fetchall()]

    # Generate script with Hermes
    script_data = await generate_podcast_script_with_chapters(dossier)

    # Next episode number
    cursor.execute("SELECT MAX(episode_number) FROM podcast_episodes;")
    max_ep = cursor.fetchone()[0]
    next_ep_num = (max_ep or 0) + 1

    episode_id = f"ep-{next_ep_num}-{uuid.uuid4().hex[:6]}"
    filename = f"dossia-episode-{next_ep_num}.mp3"
    
    # Synthesize speech
    audio_path = await TTSEngine.synthesize_speech(script_data["full_transcript"], filename)

    cursor.execute("""
    INSERT INTO podcast_episodes (
        id, dossier_id, episode_number, title, description, audio_url,
        duration_seconds, chapters, transcript
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        episode_id,
        dossier["id"],
        next_ep_num,
        script_data["episode_title"],
        f"Daily synthesized tech intelligence for {dossier['edition_date']}.",
        audio_path,
        script_data["duration_seconds"],
        json.dumps(script_data["chapters"]),
        script_data["full_transcript"]
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "episode_id": episode_id,
        "episode_number": next_ep_num,
        "title": script_data["episode_title"],
        "audio_url": audio_path,
        "duration_seconds": script_data["duration_seconds"],
        "chapters": script_data["chapters"]
    }

from pydantic import BaseModel

class SpeakRequest(BaseModel):
    title: Optional[str] = "Spoken Audio"
    text: str
    voice: Optional[str] = None

@router.post("/api/tts/speak")
async def speak_text_on_demand(payload: SpeakRequest):
    import hashlib
    text_hash = hashlib.sha256(payload.text.encode()).hexdigest()[:12]
    filename = f"speak-{text_hash}.mp3"
    
    audio_path = await TTSEngine.synthesize_speech(payload.text, filename, payload.voice)
    return {
        "status": "success",
        "audio_url": audio_path,
        "title": payload.title
    }


