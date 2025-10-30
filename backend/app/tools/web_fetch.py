"""
Jina Reader API wrapper for fetching and parsing web content.
"""
import logging
import httpx
import re
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WebFetchTool:
    """
    Tool for fetching and parsing web content using Jina Reader API.
    
    Provides async web content fetching functionality with proper error handling,
    response parsing, and logging.
    """
    
    def __init__(self):
        """Initialize the web fetch tool."""
        self.api_key = settings.JINA_READER_API_KEY
        self.base_url = "https://r.jina.ai"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=60.0,
        )
    
    def _truncate_content(self, content: str, max_words: int = 10000) -> str:
        """
        Truncate content to a maximum number of words, preserving word boundaries.
        
        Args:
            content: The content to truncate
            max_words: Maximum number of words to keep
            
        Returns:
            Truncated content string
        """
        words = content.split()
        if len(words) <= max_words:
            return content
        return " ".join(words[:max_words])
    
    def _extract_title_from_markdown(self, markdown_content: str) -> str:
        """
        Extract title from markdown content (first heading).
        
        Args:
            markdown_content: Markdown content string
            
        Returns:
            Extracted title or empty string
        """
        # Try to find first heading (# Title or ## Title)
        heading_match = re.search(r'^#+\s+(.+)$', markdown_content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()
        return ""
    
    async def fetch(
        self,
        url: str,
        mode: str = "reader"
    ) -> Dict[str, Any]:
        """
        Fetch and parse content from a URL using Jina Reader API.
        
        Args:
            url: The URL to fetch (e.g., https://example.com)
            mode: Reader mode (reader, raw, etc.) - currently only "reader" is supported
            
        Returns:
            Dictionary with url, title, content, word_count on success.
            Dictionary with "error" key on failure.
        """
        # Validate input
        if not url or not url.strip():
            logger.warning("Empty URL provided")
            return {"error": "Empty URL provided"}
        
        # Ensure URL is properly formatted
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Construct Jina API URL
        jina_url = f"{self.base_url}/{url}"
        
        logger.info(f"Fetching content from Jina Reader API: {url}")
        
        try:
            response = await self.client.get(jina_url)
            response.raise_for_status()
            
            # Jina Reader returns markdown/text content
            content = response.text
            
            # Extract title from markdown (first heading)
            title = self._extract_title_from_markdown(content)
            if not title:
                # Fallback: use URL domain or last part as title
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    title = parsed.netloc or parsed.path.split("/")[-1] or url
                except Exception:
                    title = url
            
            # Truncate content to max 10,000 words
            truncated_content = self._truncate_content(content, max_words=10000)
            
            # Calculate word count (on truncated content if it was truncated)
            word_count = len(truncated_content.split())
            
            result = {
                "url": url,
                "title": title,
                "content": truncated_content,
                "word_count": word_count,
            }
            
            logger.info(f"Successfully fetched content from {url}: {word_count} words")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Jina Reader API HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error {e.response.status_code}: Failed to fetch content"}
        except httpx.RequestError as e:
            logger.error(f"Jina Reader API request error: {e}")
            return {"error": f"Request error: Failed to fetch content"}
        except httpx.TimeoutException as e:
            logger.error(f"Jina Reader API timeout error: {e}")
            return {"error": "Request timeout: Failed to fetch content within 60 seconds"}
        except Exception as e:
            logger.error(f"Jina Reader API unexpected error: {e}", exc_info=True)
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

