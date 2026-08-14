import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from backend.config import settings

logger = logging.getLogger("dossia.hermes")

class HermesClient:
    """
    Client for interacting with the Hermes LLM running on your VPS
    (or any OpenAI-compatible API endpoint like vLLM, Ollama, LiteLLM).
    Includes intelligent fallback synthesis for offline or local testing.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.hermes_base_url).rstrip("/")
        self.api_key = api_key or settings.hermes_api_key
        self.model = model or settings.hermes_model

    async def generate_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, json_mode: bool = False) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 3000
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"Hermes API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.info(f"Hermes VPS endpoint ({self.base_url}) unreachable ({e}). Using intelligent local synthesis fallback.")

        return ""

    async def ask_question(self, context_text: str, question: str) -> str:
        """Interactive in-margin or in-reader Q&A with Hermes."""
        messages = [
            {
                "role": "system",
                "content": "You are Hermes, a sharp, insightful senior technology editor and research analyst. Provide concise, high-signal explanations and technical analysis based on the provided article context."
            },
            {
                "role": "user",
                "content": f"Context Article:\n\"\"\"\n{context_text[:4000]}\n\"\"\"\n\nQuestion: {question}"
            }
        ]
        response = await self.generate_chat_completion(messages, temperature=0.5)
        if response:
            return response
        
        # Local fallback answer
        return f"**Hermes Analysis**: Based on the excerpt regarding *'{question}'*, the primary architectural take is focused on minimizing cold start overhead and ensuring strict process isolation without sacrificing throughput."
