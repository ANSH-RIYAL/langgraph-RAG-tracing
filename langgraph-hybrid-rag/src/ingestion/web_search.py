from duckduckgo_search import DDGS
from typing import List, Dict


def web_search_news(query: str, max_results: int = 10) -> List[Dict]:
    with DDGS() as ddgs:
        results = list(ddgs.news(query, max_results=max_results))
    return results


def web_search_text(query: str, max_results: int = 10) -> List[Dict]:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results


