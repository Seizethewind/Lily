"""Optional Tavily web search (notes section 8). Never required for local inference.

The request format follows Tavily's documented REST API (Bearer auth, JSON body); verify against the
current Tavily docs and a real key before relying on it (Milestone 10).
"""
import json
import os
import urllib.error
import urllib.request

from ..utils.logging_utils import redact
from .registry import Tool

TAVILY_URL = "https://api.tavily.com/search"


class SearchUnavailable(Exception):
    pass


class TavilySearch:
    def __init__(self, api_key=None, *, timeout=15.0, post=None):
        self._key = api_key or os.environ.get("TAVILY_API_KEY")
        self._timeout = timeout
        self._post = post or self._http_post

    @property
    def available(self):
        return bool(self._key)

    def search(self, query, max_results=5, token=None):
        """Returns [{'title', 'url', 'snippet'}]. Source URLs are always preserved."""
        if not query or not query.strip():
            raise ValueError("query is empty")
        if not self._key:
            raise SearchUnavailable("Tavily API key is not configured")
        if token is not None:
            token.raise_if_cancelled()
        try:
            data = self._post({"query": query.strip(), "max_results": int(max_results)})
        except SearchUnavailable:
            raise
        except (urllib.error.URLError, OSError, ValueError) as exc:
            raise SearchUnavailable(redact(f"web search failed: {exc}", [self._key])) from None
        return [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
                for r in data.get("results", []) if r.get("url")]

    def _http_post(self, payload):
        request = urllib.request.Request(
            TAVILY_URL, data=json.dumps(payload).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self._key}"})
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            return json.loads(response.read().decode("utf-8"))


def web_search_tool(search):
    return Tool("web.search", "Search the web with Tavily (requires network access).",
                {"query": str, "max_results": int},
                lambda args, token: search.search(args["query"], args.get("max_results", 5), token),
                required=("query",))
