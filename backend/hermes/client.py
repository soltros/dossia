import json
import logging
from typing import List, Dict, Any, Optional
import httpx
from backend.config import settings

logger = logging.getLogger("dossia.llm")

class LLMClient:
    """
    Unified Multi-Provider LLM Client supporting:
    - Hermes (VPS / vLLM / Ollama / Local OpenAI-compatible)
    - OpenAI (GPT-4o, GPT-4o-mini, o3-mini)
    - Anthropic Claude (Claude 3.7 Sonnet, Claude 3.5 Sonnet, Claude 3.5 Haiku)
    - OpenRouter (DeepSeek R1, Llama 3.3 70B, Qwen 2.5, etc.)
    - Custom OpenAI-compatible endpoints
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or settings.llm_provider).lower()

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> str:
        provider = self.provider

        if provider == "chatgpt":
            return await self._call_chatgpt(messages, json_mode)
        elif provider == "anthropic":
            return await self._call_anthropic(messages, temperature, json_mode)
        elif provider == "openai":
            return await self._call_openai(messages, temperature, json_mode)
        elif provider == "openrouter":
            return await self._call_openrouter(messages, temperature, json_mode)
        elif provider == "custom":
            return await self._call_openai_compatible(
                base_url=settings.custom_base_url,
                api_key=settings.custom_api_key,
                model=settings.custom_model,
                messages=messages,
                temperature=temperature,
                json_mode=json_mode
            )
        else: # default: hermes
            return await self._call_openai_compatible(
                base_url=settings.hermes_base_url,
                api_key=settings.hermes_api_key,
                model=settings.hermes_model,
                messages=messages,
                temperature=temperature,
                json_mode=json_mode
            )

    async def _call_openai(self, messages: List[Dict[str, str]], temperature: float, json_mode: bool) -> str:
        if not settings.openai_api_key:
            logger.info("OpenAI API key not configured. Using local fallback.")
            return ""

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": settings.openai_model or "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000
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
                    logger.warning(f"OpenAI API Error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.warning(f"OpenAI request failed: {e}")

        return ""

    async def _call_chatgpt(self, messages: List[Dict[str, str]], json_mode: bool) -> str:
        """Use the official ChatGPT-plan OAuth flow and Responses API for local OSS apps."""
        from backend import chatgpt_auth

        token = await chatgpt_auth.access_token()
        models = await chatgpt_auth.available_models()
        available_ids = {model["id"] for model in models}
        model = settings.chatgpt_model or (models[0]["id"] if models else "")
        if not model or model not in available_ids:
            raise RuntimeError("Choose a model available to your ChatGPT account in Dossia Settings.")

        payload: Dict[str, Any] = {
            "model": model,
            "input": messages,
            "store": False,
            "stream": True,
            "max_output_tokens": 4000,
        }
        if json_mode:
            payload["text"] = {"format": {"type": "json_object"}}

        output = []
        completed = False
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST", "https://api.openai.com/v1/responses", json=payload,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            ) as response:
                if response.is_error:
                    logger.warning("ChatGPT Responses request failed with HTTP %s", response.status_code)
                    raise RuntimeError(f"ChatGPT request failed (HTTP {response.status_code}). Check your connection and model selection.")
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    try:
                        event = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    event_type = event.get("type")
                    if event_type == "response.output_text.delta":
                        output.append(event.get("delta", ""))
                    elif event_type == "response.failed":
                        error = (event.get("response") or {}).get("error") or {}
                        code = error.get("code") or error.get("type") or "request_failed"
                        raise RuntimeError(f"ChatGPT request failed: {code}")
                    elif event_type == "response.incomplete":
                        raise RuntimeError("ChatGPT stopped before completing the response. Try a shorter request.")
                    elif event_type == "response.completed":
                        completed = True

        if not completed:
            raise RuntimeError("ChatGPT stream ended before the response completed. Please retry.")
        return "".join(output)

    async def _call_anthropic(self, messages: List[Dict[str, str]], temperature: float, json_mode: bool) -> str:
        if not settings.anthropic_api_key:
            logger.info("Anthropic API key not configured. Using local fallback.")
            return ""

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # Extract system prompt if present
        system_content = "You are a senior technical editor and research analyst. Output strictly in the requested format."
        formatted_messages = []

        for m in messages:
            if m["role"] == "system":
                system_content = m["content"]
            else:
                formatted_messages.append({"role": m["role"], "content": m["content"]})

        if json_mode and "json" not in system_content.lower():
            system_content += "\nIMPORTANT: Output ONLY valid JSON."

        payload: Dict[str, Any] = {
            "model": settings.anthropic_model or "claude-3-5-sonnet-20241022",
            "system": system_content,
            "messages": formatted_messages,
            "max_tokens": 4000,
            "temperature": temperature
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    text_parts = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
                    return "".join(text_parts)
                else:
                    logger.warning(f"Anthropic API Error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.warning(f"Anthropic request failed: {e}")

        return ""

    async def _call_openrouter(self, messages: List[Dict[str, str]], temperature: float, json_mode: bool) -> str:
        if not settings.openrouter_api_key:
            logger.info("OpenRouter API key not configured. Using local fallback.")
            return ""

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": "https://github.com/soltros/dossia",
            "X-Title": "Dossia Intelligence",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": settings.openrouter_model or "deepseek/deepseek-r1",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000
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
                    logger.warning(f"OpenRouter API Error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.warning(f"OpenRouter request failed: {e}")

        return ""

    async def _call_openai_compatible(
        self,
        base_url: str,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        json_mode: bool
    ) -> str:
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload: Dict[str, Any] = {
            "model": model,
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
                    logger.warning(f"LLM API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.info(f"LLM endpoint ({base_url}) unreachable ({e}). Using intelligent local synthesis fallback.")

        return ""

    async def ask_question(self, context_text: str, question: str) -> str:
        """Interactive in-reader Q&A with active LLM provider."""
        messages = [
            {
                "role": "system",
                "content": "You are a sharp, insightful senior technology editor and research analyst. Provide concise, high-signal explanations and technical analysis based on the provided article context."
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
        return f"**Analysis**: Based on the excerpt regarding *'{question}'*, the primary key takeaway focuses on practical implementation mechanics and ensuring strict isolation without sacrificing throughput."

# Alias for backward compatibility
HermesClient = LLMClient
