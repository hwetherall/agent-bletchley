"""
OpenRouter/Tongyi DeepResearch client interface.
"""
import logging
import asyncio
import json
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
        stream: bool = False,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter with retry logic and tool call parsing.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            stream: Whether to stream the response (not implemented yet)
            timeout: Optional timeout in seconds (defaults to client's default timeout)
            
        Returns:
            Dictionary with keys:
            - tool_calls: List of tool call dictionaries (if any)
            - content: Final answer content (if no tool calls)
            - message: Full message object from API
            
        Raises:
            httpx.HTTPError: For API failures after retries
            ValueError: For invalid responses or missing fields
        """
        if stream:
            logger.warning("Streaming not yet implemented, falling back to non-streaming")
        
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            # Set tool_choice to "auto" to enable tool calling
            # This ensures the model will actually invoke tools when appropriate
            payload["tool_choice"] = "auto"
        
        # Use provided timeout or default client timeout
        request_timeout = timeout if timeout is not None else None
        
        # Exponential backoff retry logic: 1s, 2s, 4s delays, max 3 attempts
        max_attempts = 3
        delays = [1.0, 2.0, 4.0]
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"Sending chat completion request to {self.model} (attempt {attempt + 1}/{max_attempts})")
                if request_timeout:
                    logger.debug(f"Using custom timeout: {request_timeout}s")
                
                # Log request payload for debugging (mask sensitive data)
                payload_log = payload.copy()
                if "messages" in payload_log:
                    payload_log["messages"] = [
                        {**msg, "content": msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")}
                        for msg in payload_log["messages"]
                    ]
                logger.debug(f"Request payload: {json.dumps(payload_log, indent=2)}")
                
                # Create timeout for this request if specified
                if request_timeout:
                    timeout_obj = httpx.Timeout(request_timeout)
                    response = await self.client.post("/chat/completions", json=payload, timeout=timeout_obj)
                else:
                    response = await self.client.post("/chat/completions", json=payload)
                
                # Handle rate limiting (429) with special delay
                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", delays[min(attempt, len(delays) - 1)]))
                    if attempt < max_attempts - 1:
                        logger.warning(f"Rate limited (429), retrying after {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        response.raise_for_status()
                
                response.raise_for_status()
                
                # Parse JSON response
                try:
                    response_data = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response. Status: {response.status_code}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    logger.error(f"Response body (first 2000 chars): {response.text[:2000]}")
                    raise ValueError(f"Invalid JSON response from API: {e}")
                
                # Validate response structure
                if not response_data or "choices" not in response_data:
                    # DIAGNOSTIC LOGGING - Root cause investigation
                    logger.error(f"Missing 'choices' field in response. Status: {response.status_code}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    logger.error(f"Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
                    logger.error(f"Response body (first 2000 chars): {json.dumps(response_data, indent=2)[:2000]}")
                    
                    # Check for error fields
                    if isinstance(response_data, dict):
                        if "error" in response_data:
                            error_info = response_data.get("error", {})
                            logger.error(f"API error found: {error_info}")
                            raise ValueError(f"API error: {error_info.get('message', 'Unknown error')}")
                        if "message" in response_data:
                            logger.error(f"Response message: {response_data.get('message')}")
                    
                    raise ValueError("Invalid response structure: missing 'choices' field")
                
                if not response_data["choices"] or len(response_data["choices"]) == 0:
                    raise ValueError("Invalid response structure: empty 'choices' array")
                
                choice = response_data["choices"][0]
                if "message" not in choice:
                    raise ValueError("Invalid response structure: missing 'message' field in choice")
                
                message = choice["message"]
                
                # Log raw response for debugging
                logger.debug(f"Raw API response message: {json.dumps(message, indent=2)}")
                
                # Parse tool calls
                tool_calls = message.get("tool_calls", [])
                
                # Detect if content contains tool call descriptions instead of actual tool calls
                content = message.get("content", "")
                if content and not tool_calls:
                    # Check if content contains tool call patterns (likely a description instead of actual call)
                    tool_call_indicators = [
                        '"arguments"',
                        '"function"',
                        '"name"',
                        'tool_call',
                        'function_call'
                    ]
                    if any(indicator in content for indicator in tool_call_indicators):
                        logger.warning(
                            f"Content appears to contain tool call description instead of actual tool call. "
                            f"Content preview: {content[:200]}..."
                        )
                
                # Parse tool call arguments (may be string or dict)
                parsed_tool_calls = []
                for tool_call in tool_calls:
                    # Validate tool call structure
                    if not isinstance(tool_call, dict):
                        logger.warning(f"Invalid tool call structure (not a dict): {tool_call}")
                        continue
                    
                    if "function" not in tool_call:
                        logger.warning(f"Tool call missing 'function' field: {tool_call}")
                        continue
                    
                    parsed_call = tool_call.copy()
                    if "arguments" in parsed_call["function"]:
                        args = parsed_call["function"]["arguments"]
                        if isinstance(args, str):
                            try:
                                parsed_call["function"]["arguments"] = json.loads(args)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse tool call arguments as JSON: {args}")
                                parsed_call["function"]["arguments"] = {}
                    parsed_tool_calls.append(parsed_call)
                
                result = {
                    "tool_calls": parsed_tool_calls if parsed_tool_calls else [],
                    "content": content if content else "",
                    "message": message,
                    "usage": response_data.get("usage", {}),
                }
                
                logger.info(f"Chat completion successful. Tool calls: {len(parsed_tool_calls)}, Content length: {len(content)}")
                return result
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                status_code = e.response.status_code if e.response else None
                
                # Don't retry on 4xx errors (except 429 which is handled above)
                if status_code and 400 <= status_code < 500 and status_code != 429:
                    logger.error(f"Client error {status_code}: {e.response.text if e.response else str(e)}")
                    raise
                
                # Retry on 5xx errors and network issues
                if attempt < max_attempts - 1:
                    delay = delays[min(attempt, len(delays) - 1)]
                    logger.warning(f"HTTP error {status_code}, retrying after {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"HTTP error after {max_attempts} attempts: {e}")
                    raise
                    
            except httpx.RequestError as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    delay = delays[min(attempt, len(delays) - 1)]
                    logger.warning(f"Request error, retrying after {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Request error after {max_attempts} attempts: {e}")
                    raise
                    
            except httpx.TimeoutException as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    delay = delays[min(attempt, len(delays) - 1)]
                    logger.warning(f"Timeout error, retrying after {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Timeout error after {max_attempts} attempts: {e}")
                    raise
                    
            except (ValueError, KeyError) as e:
                # Don't retry on parsing/validation errors
                logger.error(f"Response parsing error: {e}")
                raise
                
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    delay = delays[min(attempt, len(delays) - 1)]
                    logger.warning(f"Unexpected error, retrying after {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Unexpected error after {max_attempts} attempts: {e}", exc_info=True)
                    raise
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Failed to complete request after all retries")
    
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

