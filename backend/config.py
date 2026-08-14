import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR = BASE_DIR / "storage" / "audio"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Dossia"
    db_path: str = str(DATA_DIR / "dossia.sqlite")
    hermes_base_url: str = os.getenv("HERMES_BASE_URL", "http://localhost:11434/v1")
    hermes_api_key: str = os.getenv("HERMES_API_KEY", "")
    hermes_model: str = os.getenv("HERMES_MODEL", "hermes-3-llama-3.1-8b")
    podcast_base_url: str = os.getenv("PODCAST_BASE_URL", "http://localhost:8000")
    podcast_title: str = "Dossia Daily Intelligence"
    podcast_author: str = "Dossia & Hermes"
    podcast_description: str = "Daily synthesized intelligence dossiers covering technical breakthroughs, software architecture, AI, and systems engineering."
    
settings = Settings()
