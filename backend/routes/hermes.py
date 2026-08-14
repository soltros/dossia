from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.hermes.client import HermesClient

router = APIRouter(prefix="/api/hermes", tags=["hermes"])

class AskRequest(BaseModel):
    context: str
    question: str

class SummarizeRequest(BaseModel):
    text: str

@router.post("/ask")
async def ask_hermes(payload: AskRequest):
    client = HermesClient()
    answer = await client.ask_question(payload.context, payload.question)
    return {"answer": answer}

@router.post("/summarize")
async def summarize_text(payload: SummarizeRequest):
    client = HermesClient()
    messages = [
        {"role": "system", "content": "You are Hermes. Provide a crisp 3-bullet executive TL;DR of the provided article."},
        {"role": "user", "content": payload.text[:6000]}
    ]
    summary = await client.generate_chat_completion(messages, temperature=0.5)
    return {"summary": summary}
