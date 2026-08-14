import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
MEDIA_DIR = BASE_DIR / "storage" / "audio"
SETTINGS_FILE = DATA_DIR / "settings.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Dossia"
    db_path: str = str(DATA_DIR / "dossia.sqlite")
    
    # Active LLM Provider: 'hermes', 'openai', 'anthropic', 'openrouter', 'custom'
    llm_provider: str = os.getenv("LLM_PROVIDER", "hermes")
    
    # Hermes / Local / VPS (OpenAI-compatible)
    hermes_base_url: str = os.getenv("HERMES_BASE_URL", "http://localhost:11434/v1")
    hermes_api_key: str = os.getenv("HERMES_API_KEY", "")
    hermes_model: str = os.getenv("HERMES_MODEL", "hermes-3-llama-3.1-8b")
    
    # OpenAI API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Anthropic Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # OpenRouter API
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1")
    
    # Custom Endpoint
    custom_base_url: str = os.getenv("CUSTOM_BASE_URL", "http://localhost:8080/v1")
    custom_api_key: str = os.getenv("CUSTOM_API_KEY", "")
    custom_model: str = os.getenv("CUSTOM_MODEL", "default")
    
    # Podcasting 2.0
    podcast_base_url: str = os.getenv("PODCAST_BASE_URL", "http://localhost:8000")
    podcast_title: str = "Dossia Daily Intelligence"
    podcast_author: str = "Dossia Editorial Desk"
    podcast_description: str = "Daily synthesized intelligence dossiers covering technical breakthroughs, systems architecture, Linux, local AI, and labor."

    def load_persisted(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if hasattr(self, k) and v is not None:
                            setattr(self, k, v)
            except Exception as e:
                pass

    def save_persisted(self):
        try:
            data = {
                "llm_provider": self.llm_provider,
                "hermes_base_url": self.hermes_base_url,
                "hermes_api_key": self.hermes_api_key,
                "hermes_model": self.hermes_model,
                "openai_api_key": self.openai_api_key,
                "openai_model": self.openai_model,
                "anthropic_api_key": self.anthropic_api_key,
                "anthropic_model": self.anthropic_model,
                "openrouter_api_key": self.openrouter_api_key,
                "openrouter_model": self.openrouter_model,
                "custom_base_url": self.custom_base_url,
                "custom_api_key": self.custom_api_key,
                "custom_model": self.custom_model,
                "podcast_base_url": self.podcast_base_url
            }
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            pass

settings = Settings()
settings.load_persisted()
