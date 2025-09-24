from __future__ import annotations
import os
from typing import List, Dict, Any, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

class NewsProviderError(Exception):
    pass

class NewsAPIProvider:
    """NewsAPI.org provider (requires NEWSAPI_KEY env)."""
    BASE = "https://newsapi.org/v2"
    CATEGORY_MAP = {"technology": "technology", "finance": "business", "sports": "sports"}

    def __init__(self, api_key: Optional[str] = None, country: str = "us"):
        self.api_key = api_key or os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")
        self.country = country

    def enabled(self) -> bool:
        return bool(self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(1, 3))
    def top_headlines(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.enabled():
            raise NewsProviderError("NewsAPI key missing. Set NEWSAPI_KEY.")
        mapped = self.CATEGORY_MAP.get(category) or None
        if mapped is None:
            return self.search(query=category, limit=limit)
        r = requests.get(f"{self.BASE}/top-headlines", params={
            "apiKey": self.api_key, "category": mapped, "pageSize": min(limit, 100),
            "language": "en", "country": self.country
        }, timeout=20)
        if r.status_code != 200:
            raise NewsProviderError(f"NewsAPI error: {r.status_code} {r.text}")
        data = r.json().get("articles", [])[:limit]
        return [{
            "title": a.get("title"),
            "source": (a.get("source") or {}).get("name"),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt"),
            "description": a.get("description"),
            "content": a.get("content"),
            "provider": "newsapi"
        } for a in data]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(1, 3))
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.enabled():
            raise NewsProviderError("NewsAPI key missing. Set NEWSAPI_KEY.")
        r = requests.get(f"{self.BASE}/everything", params={
            "apiKey": self.api_key, "q": query, "pageSize": min(limit, 100),
            "language": "en", "sortBy": "publishedAt"
        }, timeout=20)
        if r.status_code != 200:
            raise NewsProviderError(f"NewsAPI error: {r.status_code} {r.text}")
        data = r.json().get("articles", [])[:limit]
        return [{
            "title": a.get("title"),
            "source": (a.get("source") or {}).get("name"),
            "url": a.get("url"),
            "publishedAt": a.get("publishedAt"),
            "description": a.get("description"),
            "content": a.get("content"),
            "provider": "newsapi"
        } for a in data]
