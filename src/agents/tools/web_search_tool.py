from duckduckgo_search import DDGS
import logging
from typing import Dict, Any

logger = logging.getLogger("zyntra.web_search_tool")

def web_search_tool(query: str, max_results: int = 5) -> str:
    """Searches the live internet for up-to-date information, news, or facts. Provide a concise search query. Use this ONLY when the user asks for current events or real-time web data."""
    try:
        results = []
        with DDGS() as ddgs:
            # text() returns a generator
            for idx, r in enumerate(ddgs.text(query, max_results=max_results)):
                results.append(f"Result {idx+1}:\nTitle: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}\n")
        
        if not results:
            return f"No results found on the web for query: '{query}'."
            
        return "\n".join(results)
    except Exception as e:
        logger.error(f"Error in web search tool: {e}")
        return f"Error performing web search: {str(e)}"
