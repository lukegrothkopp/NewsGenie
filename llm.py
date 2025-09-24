from __future__ import annotations
import os, json
from typing import Dict, Any
from openai import OpenAI
from prompts import SYSTEM_CLASSIFIER, SYSTEM_SUMMARIZER, SYSTEM_ANSWER

def get_client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Missing OPENAI_API_KEY. Set it before launch.")
    return OpenAI()

def classify_intent(message: str) -> Dict[str, Any]:
    client = get_client()
    msg = [{"role": "system", "content": SYSTEM_CLASSIFIER},
           {"role": "user", "content": message}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msg, temperature=0)
    text = resp.choices[0].message.content
    try:
        data = json.loads(text)
        return {"intent": data.get("intent","general"), "category": data.get("category","other"), "reasoning": data.get("reasoning","")}
    except Exception:
        return {"intent": "general", "category": "other", "reasoning": "fallback_json_parse"}

def summarize_news(context: str, user_query: str) -> str:
    client = get_client()
    msg = [{"role": "system", "content": SYSTEM_SUMMARIZER},
           {"role": "user", "content": f"User asked: {user_query}\n\nArticles:\n{context}"}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msg, temperature=0.2)
    return resp.choices[0].message.content

def answer_general(question: str) -> str:
    client = get_client()
    msg = [{"role": "system", "content": SYSTEM_ANSWER},
           {"role": "user", "content": question}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msg, temperature=0)
    return resp.choices[0].message.content
