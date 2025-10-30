"""
Tool registry for defining available tools for the AI agent.
"""
from typing import List, Dict, Any
from app.tools.web_search import WebSearchTool
from app.tools.web_fetch import WebFetchTool


class ToolRegistry:
    """
    Registry of available tools for the research agent.
    
    Defines tool schemas compatible with OpenRouter function calling.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self.web_search = WebSearchTool()
        self.web_fetch = WebFetchTool()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in OpenRouter function calling format.
        
        Returns:
            List of tool definition dictionaries
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": (
                        "INVOKE THIS TOOL to search the web for information using Brave Search. "
                        "You MUST call this function (not describe it) when you need to find sources. "
                        "Returns search results with URLs, titles, and snippets. "
                        "Use this FIRST to discover relevant articles and pages about a topic."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of results to return (default: 10, max: 20)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_fetch",
                    "description": (
                        "INVOKE THIS TOOL to fetch and parse content from a web URL. "
                        "You MUST call this function (not describe it) when you need to read full article content. "
                        "Returns the parsed text content, title, and metadata. "
                        "Use this AFTER web_search to read articles and pages you found."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch and parse"
                            },
                            "mode": {
                                "type": "string",
                                "description": "Reader mode: 'reader' for parsed content, 'raw' for raw HTML",
                                "enum": ["reader", "raw"],
                                "default": "reader"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        if tool_name == "web_search":
            query = parameters.get("query")
            count = parameters.get("count", 10)
            results = await self.web_search.search(query=query, count=count)
            return {
                "tool": "web_search",
                "results": results
            }
        elif tool_name == "web_fetch":
            url = parameters.get("url")
            mode = parameters.get("mode", "reader")
            content = await self.web_fetch.fetch(url=url, mode=mode)
            return {
                "tool": "web_fetch",
                "content": content
            }
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

