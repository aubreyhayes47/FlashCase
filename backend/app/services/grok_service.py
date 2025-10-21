"""
Grok AI service integration with CourtListener legal database.

This service provides AI-powered legal assistance by integrating xAI's Grok model
with CourtListener's case law database for verifiable legal sources.
"""

import json
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.core.config import settings


async def search_courtlistener(
    query: str,
    court: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Search CourtListener API for legal cases and opinions.
    
    This tool searches the CourtListener database for relevant legal cases
    based on the provided query. Results include case names, citations,
    court information, and summaries.
    
    Args:
        query: Search query for legal cases (e.g., "Fourth Amendment search warrant")
        court: Optional court identifier to filter results (e.g., "scotus" for Supreme Court)
        jurisdiction: Optional jurisdiction filter (e.g., "federal", "state")
        max_results: Maximum number of results to return (default: 5, max: 20)
    
    Returns:
        Dictionary containing search results with case information:
        - count: Total number of results found
        - results: List of case details including name, citation, court, date, and summary
    
    Example:
        >>> results = await search_courtlistener("Miranda rights", court="scotus", max_results=3)
        >>> print(results['results'][0]['case_name'])
    """
    # Validate max_results
    max_results = min(max(1, max_results), 20)
    
    # Build search parameters
    params = {
        "q": query,
        "type": "o",  # Opinion search
        "order_by": "score desc",
        "stat_Precedential": "on",  # Only precedential opinions
    }
    
    if court:
        params["court"] = court
    
    # Make request to CourtListener API
    headers = {}
    if settings.courtlistener_api_key:
        headers["Authorization"] = f"Token {settings.courtlistener_api_key}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{settings.courtlistener_api_base_url}/search/",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            # Format results
            results = []
            for item in data.get("results", [])[:max_results]:
                results.append({
                    "case_name": item.get("caseName", ""),
                    "citation": item.get("citation", []),
                    "court": item.get("court", ""),
                    "date_filed": item.get("dateFiled", ""),
                    "summary": item.get("snippet", ""),
                    "url": f"https://www.courtlistener.com{item.get('absolute_url', '')}"
                })
            
            return {
                "count": data.get("count", 0),
                "results": results
            }
            
        except httpx.HTTPError as e:
            return {
                "error": f"CourtListener API error: {str(e)}",
                "count": 0,
                "results": []
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "count": 0,
                "results": []
            }


class GrokService:
    """
    Service for interacting with xAI's Grok API with tool calling capabilities.
    
    This service provides methods for chat completion, card generation, and
    AI-assisted content creation, all grounded in legal sources via CourtListener.
    
    Includes token usage tracking for cost monitoring and control.
    """
    
    # Class-level token usage tracking
    _token_usage = {
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "total_requests": 0
    }
    
    def __init__(self):
        """Initialize the Grok service with API configuration."""
        self.api_key = settings.grok_api_key
        self.api_base_url = settings.grok_api_base_url
        self.model = settings.grok_model
        
        # Initialize per-instance tracking
        self.request_token_count = 0
        
        # Define the CourtListener search tool schema
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_courtlistener",
                    "description": "Search CourtListener API for legal cases, opinions, and precedents. Use this to find relevant case law, citations, and legal sources to support legal analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for legal cases (e.g., 'Fourth Amendment search warrant', 'Miranda v. Arizona')"
                            },
                            "court": {
                                "type": "string",
                                "description": "Optional court identifier (e.g., 'scotus' for Supreme Court, 'ca9' for 9th Circuit)"
                            },
                            "jurisdiction": {
                                "type": "string",
                                "description": "Optional jurisdiction filter (e.g., 'federal', 'state')"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 5, max: 20)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def _track_token_usage(self, usage_data: Dict[str, Any]) -> None:
        """
        Track token usage from API responses for monitoring and cost control.
        
        Args:
            usage_data: Usage data from API response containing token counts
        """
        if not settings.token_usage_tracking_enabled:
            return
        
        if usage_data:
            prompt_tokens = usage_data.get("prompt_tokens", 0)
            completion_tokens = usage_data.get("completion_tokens", 0)
            total_tokens = usage_data.get("total_tokens", 0)
            
            # Update class-level tracking
            GrokService._token_usage["total_prompt_tokens"] += prompt_tokens
            GrokService._token_usage["total_completion_tokens"] += completion_tokens
            GrokService._token_usage["total_tokens"] += total_tokens
            GrokService._token_usage["total_requests"] += 1
            
            # Update instance tracking
            self.request_token_count += total_tokens
    
    @classmethod
    def get_token_usage_stats(cls) -> Dict[str, Any]:
        """
        Get current token usage statistics for monitoring.
        
        Returns:
            Dictionary containing token usage statistics
        """
        return cls._token_usage.copy()
    
    @classmethod
    def reset_token_usage_stats(cls) -> None:
        """Reset token usage statistics (useful for testing or periodic resets)."""
        cls._token_usage = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_requests": 0
        }
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call by name with provided arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
        
        Returns:
            Tool execution results
        """
        if tool_name == "search_courtlistener":
            return await search_courtlistener(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = None,
        max_tokens: int = None
    ) -> AsyncGenerator[str, None]:
        """
        Send chat completion request to Grok with tool calling support.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response
            temperature: Sampling temperature (0.0 to 2.0), defaults to cost-controlled value
            max_tokens: Maximum tokens in response, defaults to cost-controlled value
        
        Yields:
            Response chunks as they arrive (if streaming)
            or complete response (if not streaming)
        """
        if not self.api_key:
            yield json.dumps({"error": "Grok API key not configured"})
            return
        
        # Use cost-controlled defaults if not specified
        if temperature is None:
            temperature = settings.grok_default_temperature
        if max_tokens is None:
            max_tokens = settings.grok_chat_max_tokens
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "tools": self.tools,
            "tool_choice": "auto"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                if stream:
                    # Streaming response
                    async with client.stream(
                        "POST",
                        f"{self.api_base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:
                        response.raise_for_status()
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    break
                                
                                try:
                                    chunk = json.loads(data)
                                    
                                    # Handle tool calls
                                    if chunk.get("choices", [{}])[0].get("delta", {}).get("tool_calls"):
                                        tool_calls = chunk["choices"][0]["delta"]["tool_calls"]
                                        for tool_call in tool_calls:
                                            if tool_call.get("function"):
                                                function_name = tool_call["function"]["name"]
                                                function_args = json.loads(tool_call["function"]["arguments"])
                                                
                                                # Execute tool
                                                tool_result = await self._call_tool(function_name, function_args)
                                                
                                                # Send tool result back to model
                                                messages.append({
                                                    "role": "assistant",
                                                    "content": None,
                                                    "tool_calls": [{
                                                        "id": tool_call.get("id"),
                                                        "type": "function",
                                                        "function": {
                                                            "name": function_name,
                                                            "arguments": json.dumps(function_args)
                                                        }
                                                    }]
                                                })
                                                messages.append({
                                                    "role": "tool",
                                                    "tool_call_id": tool_call.get("id"),
                                                    "content": json.dumps(tool_result)
                                                })
                                                
                                                # Continue conversation with tool result
                                                async for subsequent_chunk in self.chat_completion(
                                                    messages, stream=True, temperature=temperature, max_tokens=max_tokens
                                                ):
                                                    yield subsequent_chunk
                                                return
                                    
                                    # Regular content chunk
                                    if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                                        yield chunk["choices"][0]["delta"]["content"]
                                        
                                except json.JSONDecodeError:
                                    continue
                else:
                    # Non-streaming response
                    response = await client.post(
                        f"{self.api_base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Track token usage
                    if data.get("usage"):
                        self._track_token_usage(data["usage"])
                    
                    # Handle tool calls in non-streaming mode
                    if data.get("choices", [{}])[0].get("message", {}).get("tool_calls"):
                        tool_calls = data["choices"][0]["message"]["tool_calls"]
                        
                        for tool_call in tool_calls:
                            function_name = tool_call["function"]["name"]
                            function_args = json.loads(tool_call["function"]["arguments"])
                            
                            # Execute tool
                            tool_result = await self._call_tool(function_name, function_args)
                            
                            # Add tool interaction to messages
                            messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [tool_call]
                            })
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps(tool_result)
                            })
                        
                        # Get final response with tool results
                        async for chunk in self.chat_completion(
                            messages, stream=False, temperature=temperature, max_tokens=max_tokens
                        ):
                            yield chunk
                        return
                    
                    # Return complete response
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    yield content
                    
            except httpx.HTTPError as e:
                yield json.dumps({"error": f"Grok API error: {str(e)}"})
            except Exception as e:
                yield json.dumps({"error": f"Unexpected error: {str(e)}"})
    
    async def rewrite_card(
        self,
        front: str,
        back: str,
        instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Use Grok to improve or rewrite a flashcard.
        
        Args:
            front: Current front of the card (question)
            back: Current back of the card (answer)
            instruction: Optional instruction for how to rewrite (e.g., "make it more concise")
        
        Yields:
            Streaming JSON with suggested improvements
        """
        prompt = f"""You are a legal education assistant helping law students create effective flashcards.

Current flashcard:
Front: {front}
Back: {back}

{f"User instruction: {instruction}" if instruction else ""}

Please suggest improvements to make this flashcard more effective for studying. Consider:
1. Clarity and precision of the question
2. Completeness and accuracy of the answer
3. Proper legal citations and sources (use search_courtlistener if needed)
4. Appropriate level of detail for law school study

Provide your response in JSON format:
{{
    "front": "improved question",
    "back": "improved answer",
    "explanation": "brief explanation of changes made",
    "sources": ["relevant case citations"]
}}"""

        messages = [
            {"role": "system", "content": "You are a legal education expert who helps law students create effective study materials. You have access to CourtListener to find relevant case law and citations."},
            {"role": "user", "content": prompt}
        ]
        
        # Use cost-controlled defaults for rewriting (lower temperature for consistency, fewer tokens)
        async for chunk in self.chat_completion(
            messages, 
            stream=True, 
            temperature=0.5,
            max_tokens=settings.grok_rewrite_max_tokens
        ):
            yield chunk
    
    async def autocomplete_card(
        self,
        partial_text: str,
        card_type: str = "front"
    ) -> AsyncGenerator[str, None]:
        """
        Provide AI-powered autocomplete suggestions for card creation.
        
        Args:
            partial_text: Partial text entered by user
            card_type: Either "front" (question) or "back" (answer)
        
        Yields:
            Streaming completion suggestions
        """
        if card_type == "front":
            prompt = f"""Based on this partial legal question: "{partial_text}"

Suggest 3 complete, well-formed legal study questions. Use search_courtlistener if you need to reference specific cases or doctrines.

Format your response as JSON:
{{
    "suggestions": [
        "complete question 1",
        "complete question 2", 
        "complete question 3"
    ]
}}"""
        else:  # back
            prompt = f"""Based on this partial legal answer: "{partial_text}"

Complete this answer with accurate legal information. Include relevant case citations using search_courtlistener if appropriate.

Format your response as JSON:
{{
    "completion": "completed answer with citations"
}}"""
        
        messages = [
            {"role": "system", "content": "You are a legal education expert helping law students create study materials. Provide accurate, well-cited legal information."},
            {"role": "user", "content": prompt}
        ]
        
        # Use cost-controlled defaults for autocomplete (low temperature, minimal tokens)
        async for chunk in self.chat_completion(
            messages, 
            stream=True, 
            temperature=0.3,
            max_tokens=settings.grok_autocomplete_max_tokens
        ):
            yield chunk
