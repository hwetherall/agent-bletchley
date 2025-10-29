"""
OpenRouter/Tongyi DeepResearch client interface.
"""
import logging
import httpx
from typing import Dict, List, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TongyiClient:
    """
    Client for interacting with OpenRouter API for Tongyi DeepResearch.
    
    TODO: Implement full integration with OpenRouter API:
    1. Chat completions with tool calling support
    2. Streaming responses for real-time updates
    3. Tool definitions from ToolRegistry
    4. Error handling and retries
    """
    
    def __init__(self):
        """Initialize the Tongyi client."""
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.TONGYI_MODEL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/agent-bletchley",
                "X-Title": "Agent Bletchley",
            },
            timeout=60.0,
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            stream: Whether to stream the response
            
        Returns:
            API response dictionary
        """
        # TODO: Implement chat completion with tool calling
        # TODO: Handle streaming responses if stream=True
        # TODO: Parse tool calls from response
        # TODO: Implement retry logic for failed requests
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
        
        if stream:
            payload["stream"] = True
        
        logger.info(f"Sending chat completion request to {self.model}")
        
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
    
    async def send_research_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a research query to the Tongyi agent.
        
        Args:
            query: The research question/query
            context: Optional context from previous research steps
            
        Returns:
            Agent response with potential tool calls
        """
        # TODO: Format research query with context
        # TODO: Include available tools from ToolRegistry
        # TODO: Parse agent response for tool calls or final answer
        
        messages = [
            {
                "role": "system",
                "content": "You are a research assistant for investment due diligence. Use available tools to gather comprehensive information."
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        tools = []  # TODO: Get tools from ToolRegistry
        
        return await self.chat_completion(messages=messages, tools=tools)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

