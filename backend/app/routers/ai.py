"""
AI endpoints for chat, card rewriting, and autocomplete using Grok.

These endpoints provide AI-powered features for legal flashcard creation
and study assistance, with rate limiting to control usage.

Security Note: All exception handling in this module has been designed to
prevent stack trace exposure. Generic error messages are returned to users
while detailed errors are logged for debugging.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.services.grok_service import GrokService
from app.core.config import settings
import json
import logging

router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize Grok service
grok_service = GrokService()

# Setup logging for internal debugging
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    stream: bool = Field(default=True, description="Whether to stream the response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2000, ge=1, le=4096, description="Maximum tokens in response")


class RewriteCardRequest(BaseModel):
    """Request model for card rewriting."""
    front: str = Field(..., description="Current front of the card (question)")
    back: str = Field(..., description="Current back of the card (answer)")
    instruction: Optional[str] = Field(None, description="Optional instruction for rewriting")


class AutocompleteCardRequest(BaseModel):
    """Request model for card autocomplete."""
    partial_text: str = Field(..., description="Partial text entered by user")
    card_type: str = Field(..., description="Either 'front' or 'back'")


async def event_generator(generator):
    """
    Convert async generator to SSE format with secure error handling.
    
    This function ensures that no internal error details or stack traces
    are exposed to external users. All exceptions are caught and logged
    internally while returning generic error messages to the client.
    
    Args:
        generator: Async generator yielding content chunks
    
    Yields:
        SSE-formatted data strings
    """
    try:
        async for chunk in generator:
            if chunk:
                # Format as Server-Sent Event
                yield f"data: {json.dumps({'content': chunk})}\n\n"
    except Exception as e:
        # Log internal error for debugging (not exposed to user)
        logger.error(f"Error in event generator: {e}", exc_info=True)
        # Return generic error message to user
        yield f"data: {json.dumps({'error': 'An error occurred while processing your request'})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(request: ChatRequest, http_request: Request):
    """
    Chat with Grok AI assistant with CourtListener integration.
    
    This endpoint provides conversational AI assistance for legal questions,
    with automatic grounding in CourtListener case law when relevant.
    
    - **messages**: List of chat messages (role and content)
    - **stream**: Whether to stream the response (default: true)
    - **temperature**: Controls randomness (0.0-2.0, default: 0.7)
    - **max_tokens**: Maximum tokens in response (1-4096, default: 2000)
    
    Returns streaming response (SSE) if stream=true, otherwise JSON response.
    """
    if not settings.grok_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set GROK_API_KEY."
        )
    
    # Convert Pydantic models to dicts
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Add system message if not present
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {
            "role": "system",
            "content": "You are a legal AI assistant for law students. You have access to CourtListener's case law database. Provide accurate, well-cited legal information and help students create effective study materials."
        })
    
    try:
        generator = grok_service.chat_completion(
            messages=messages,
            stream=request.stream,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if request.stream:
            return StreamingResponse(
                event_generator(generator),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Collect full response for non-streaming
            full_response = ""
            async for chunk in generator:
                full_response += chunk
            
            try:
                # Try to parse as JSON if it's a structured response
                response_json = json.loads(full_response)
                return response_json
            except json.JSONDecodeError:
                # Return as plain text if not JSON
                return {"content": full_response}
    
    except Exception as e:
        # Log internal error for debugging (not exposed to user)
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        # Don't expose internal error details to external users
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")


@router.post("/rewrite-card")
async def rewrite_card(request: RewriteCardRequest, http_request: Request):
    """
    Use AI to improve or rewrite a flashcard.
    
    Provides suggestions for improving flashcard quality, including:
    - Clarity and precision of questions
    - Completeness and accuracy of answers
    - Proper legal citations and sources
    - Appropriate level of detail
    
    - **front**: Current front of the card (question)
    - **back**: Current back of the card (answer)
    - **instruction**: Optional instruction for how to rewrite
    
    Returns streaming response (SSE) with suggested improvements.
    """
    if not settings.grok_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set GROK_API_KEY."
        )
    
    try:
        generator = grok_service.rewrite_card(
            front=request.front,
            back=request.back,
            instruction=request.instruction
        )
        
        return StreamingResponse(
            event_generator(generator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        # Log internal error for debugging (not exposed to user)
        logger.error(f"Error in rewrite-card endpoint: {e}", exc_info=True)
        # Don't expose internal error details to external users
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")


@router.post("/autocomplete-card")
async def autocomplete_card(request: AutocompleteCardRequest, http_request: Request):
    """
    Provide AI-powered autocomplete suggestions for card creation.
    
    Helps users create cards faster by suggesting completions based on
    partial text input. Uses CourtListener when appropriate for citations.
    
    - **partial_text**: Partial text entered by user
    - **card_type**: Either "front" (question) or "back" (answer)
    
    Returns streaming response (SSE) with completion suggestions.
    """
    if not settings.grok_api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service not configured. Please set GROK_API_KEY."
        )
    
    if request.card_type not in ["front", "back"]:
        raise HTTPException(
            status_code=400,
            detail="card_type must be either 'front' or 'back'"
        )
    
    try:
        generator = grok_service.autocomplete_card(
            partial_text=request.partial_text,
            card_type=request.card_type
        )
        
        return StreamingResponse(
            event_generator(generator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except Exception as e:
        # Log internal error for debugging (not exposed to user)
        logger.error(f"Error in autocomplete-card endpoint: {e}", exc_info=True)
        # Don't expose internal error details to external users
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")


@router.get("/health")
async def ai_health_check():
    """
    Check AI service configuration and availability.
    
    Returns status of Grok API and CourtListener API configuration.
    """
    return {
        "status": "healthy",
        "grok_configured": bool(settings.grok_api_key),
        "courtlistener_configured": bool(settings.courtlistener_api_key),
        "model": settings.grok_model,
        "rate_limiting_enabled": settings.rate_limit_enabled
    }
