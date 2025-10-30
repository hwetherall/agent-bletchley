"""
Brave Search API wrapper for web search functionality.
"""
import logging
import httpx
from typing import List, Dict, Any, Optional, Union
from app.config import settings

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Tool for performing web searches using Brave Search API.
    
    Provides async web search functionality with proper error handling,
    response parsing, and logging.
    """
    
    def __init__(self):
        """Initialize the web search tool."""
        self.api_key = settings.BRAVE_SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1"
        self.client = httpx.AsyncClient(
            headers={
                "X-Subscription-Token": self.api_key,
            },
            timeout=30.0,
        )
    
    async def search(
        self,
        query: Union[str, List[str]],
        count: int = 10,
        offset: int = 0,
        safesearch: str = "moderate"
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search.
        
        Args:
            query: Search query string or list of query strings (if list, uses first element)
            count: Number of results to return (max 20)
            offset: Offset for pagination
            safesearch: Safe search setting (off, moderate, strict)
            
        Returns:
            List of search result dictionaries with title, url, snippet.
            Returns empty list on error.
        """
        # Handle array queries from Tongyi (convert to single string)
        if isinstance(query, list):
            if not query:
                logger.warning("Empty query list provided")
                return []
            if len(query) > 1:
                logger.warning(f"Tongyi sent multiple queries: {query}. Using first query: {query[0]}")
            query = query[0]
        
        # Validate input
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []
        
        # Limit count to max 10 per requirements
        count = min(count, 10)
        
        logger.info(f"Searching Brave Search API for: {query} (count={count})")
        
        params = {
            "q": query,
            "count": min(count, 20),  # Brave API supports up to 20, but we cap at 10
            "offset": offset,
            "safesearch": safesearch,
        }
        
        url = f"{self.base_url}/web/search"
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Parse and format results
            raw_results = data.get("web", {}).get("results", [])
            
            # Extract and format results
            results = []
            for item in raw_results[:count]:
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                }
                # Only add result if it has required fields
                if result["title"] and result["url"]:
                    results.append(result)
            
            logger.info(f"Brave Search API returned {len(results)} results for query: {query}")
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Brave Search API HTTP error: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Brave Search API request error: {e}")
            return []
        except httpx.TimeoutException as e:
            logger.error(f"Brave Search API timeout error: {e}")
            return []
        except Exception as e:
            logger.error(f"Brave Search API unexpected error: {e}", exc_info=True)
            return []
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

