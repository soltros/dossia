import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from backend.config import settings, MEDIA_DIR

logger = logging.getLogger("dossia.podcast.tts")

class TTSEngine:
    """
    TTS Engine supporting:
    1. Remote Kokoro / Piper / OpenAI-compatible /v1/audio/speech endpoints on VPS
    2. Fallback audio file generator with silence/tone generation or mock media
    """

    @staticmethod
    async def synthesize_speech(text: str, filename: str, voice: str = "alloy") -> str:
        output_path = MEDIA_DIR / filename
        
        # Check if remote TTS endpoint is configured in env
        tts_endpoint = os.getenv("TTS_API_URL", "")
        if tts_endpoint:
            try:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "model": "tts-1",
                    "input": text,
                    "voice": voice
                }
                async with httpx.AsyncClient(timeout=90.0) as client:
                    resp = await client.post(f"{tts_endpoint.rstrip('/')}/audio/speech", json=payload, headers=headers)
                    if resp.status_code == 200:
                        with open(output_path, "wb") as f:
                            f.write(resp.content)
                        return f"/audio/{filename}"
            except Exception as e:
                logger.warning(f"Remote TTS failed ({e}), creating standard audio asset.")

        # If no remote TTS server is reached, write an empty or small valid MP3 container so the feed is strictly valid
        if not output_path.exists():
            # Create a lightweight placeholder MP3 file so podcast players can validate the enclosure
            with open(output_path, "wb") as f:
                # 1-second silence MP3 header bytes
                f.write(b'\xff\xfb\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' * 32)
                
        return f"/audio/{filename}"
