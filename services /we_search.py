from __future__ import annotations
import os
from typing import List, Dict, Any, Optional
import requests

class WebSearchError(Exception):
    pass

class TavilySearch:
    """Tavily web search (requires TAVILY_API_KEY)."""
    BASE = "https://api.tavily.com/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

    def enabled(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.enabled():
            raise WebSearchError("Tavily API key missing. Set TAVILY_API_KEY.")
        payload = {"api_key": self.api_key, "query": query, "include_domains": [], "max_results": max_results}
        r = requests.post(self.BASE, json=payload, timeout=20)
        if r.status_code != 200:
            raise WebSearchError(f"Tavily error: {r.status_code} {r.text}")
        return r.json().get("results", [])
