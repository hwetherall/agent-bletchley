"""
Jina Reader API wrapper for fetching and parsing web content.
"""
import logging
import httpx
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WebFetchTool:
    """
    Tool for fetching and parsing web content using Jina Reader API.
    
    TODO: Implement full Jina Reader integration:
    1. Fetch article/content from URL
    2. Parse and extract main content
    3. Handle different content types
    4. Extract metadata (title, author, date, etc.)
    """
    
    def __init__(self):
        """Initialize the web fetch tool."""
        self.api_key = settings.JINA_READER_API_KEY
        self.base_url = "https://r.jina.ai"
        self.client = httpx.AsyncClient(
            headers={
                "X-RapidAPI-Key": self.api_key,
            },
            timeout=60.0,
        )
    
    async def fetch(
        self,
        url: str,
        mode: str = "reader"
    ) -> Dict[str, Any]:
        """
        Fetch and parse content from a URL.
        
        Args:
            url: The URL to fetch
            mode: Reader mode (reader, raw, etc.)
            
        Returns:
            Dictionary with parsed content, title, metadata, etc.
        """
        # TODO: Implement actual Jina Reader API call
        # TODO: Parse response and extract content
        # TODO: Handle different modes and options
        # TODO: Extract metadata fields
        # TODO: Handle errors (404, timeout, etc.)
        
        logger.info(f"Fetching content from: {url}")
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
        }
        
        if mode == "reader":
            headers["X-Return-Format"] = "json"
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            # TODO: Parse response based on format
            if mode == "reader":
                return response.json()
            else:
                return {
                    "url": url,
                    "content": response.text,
                    "status_code": response.status_code,
                }
        except httpx.HTTPError as e:
            logger.error(f"Jina Reader API error: {e}")
            raise
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

