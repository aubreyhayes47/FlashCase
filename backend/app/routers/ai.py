"""
AI endpoints for chat, card rewriting, and autocomplete using Grok.

These endpoints provide AI-powered features for legal flashcard creation
and study assistance, with rate limiting to control usage.

Security Note: All exception handling in this module has been designed to
prevent stack trace exposure. Generic error messages are returned to users
while detailed errors are logged for debugging.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.services.grok_service import GrokService
from app.core.config import settings
from app.middleware.rate_limit import limiter
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
@limiter.limit(f"{settings.ai_rate_limit_per_minute}/minute")
@limiter.limit(f"{settings.ai_rate_limit_per_hour}/hour")
async def chat(request: Request, chat_request: ChatRequest):
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
    messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]
    
    # Add system message if not present
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {
            "role": "system",
            "content": "You are a legal AI assistant for law students. You have access to CourtListener's case law database. Provide accurate, well-cited legal information and help students create effective study materials."
        })
    
    try:
        generator = grok_service.chat_completion(
            messages=messages,
            stream=chat_request.stream,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens
        )
        
        if chat_request.stream:
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
@limiter.limit(f"{settings.ai_rate_limit_per_minute}/minute")
@limiter.limit(f"{settings.ai_rate_limit_per_hour}/hour")
async def rewrite_card(request: Request, card_request: RewriteCardRequest):
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
            front=card_request.front,
            back=card_request.back,
            instruction=card_request.instruction
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
@limiter.limit(f"{settings.ai_rate_limit_per_minute}/minute")
@limiter.limit(f"{settings.ai_rate_limit_per_hour}/hour")
async def autocomplete_card(request: Request, autocomplete_request: AutocompleteCardRequest):
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
    
    if autocomplete_request.card_type not in ["front", "back"]:
        raise HTTPException(
            status_code=400,
            detail="card_type must be either 'front' or 'back'"
        )
    
    try:
        generator = grok_service.autocomplete_card(
            partial_text=autocomplete_request.partial_text,
            card_type=autocomplete_request.card_type
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
        "rate_limiting_enabled": settings.rate_limit_enabled,
        "ai_rate_limits": {
            "per_minute": settings.ai_rate_limit_per_minute,
            "per_hour": settings.ai_rate_limit_per_hour
        }
    }


@router.get("/usage")
async def get_token_usage():
    """
    Get token usage statistics for monitoring and cost control.
    
    Returns current token usage metrics including:
    - Total prompt tokens used
    - Total completion tokens used
    - Total tokens consumed
    - Total number of requests made
    - Alert threshold status
    
    This endpoint helps monitor AI costs and can be used for alerting
    when usage exceeds configured thresholds.
    """
    if not settings.token_usage_tracking_enabled:
        raise HTTPException(
            status_code=503,
            detail="Token usage tracking is not enabled"
        )
    
    usage_stats = GrokService.get_token_usage_stats()
    
    # Check if usage exceeds alert threshold
    alert_triggered = usage_stats["total_tokens"] >= settings.token_usage_alert_threshold
    
    return {
        "usage": usage_stats,
        "alert_threshold": settings.token_usage_alert_threshold,
        "alert_triggered": alert_triggered,
        "cost_control": {
            "model": settings.grok_model,
            "default_temperature": settings.grok_default_temperature,
            "max_tokens": {
                "chat": settings.grok_chat_max_tokens,
                "rewrite": settings.grok_rewrite_max_tokens,
                "autocomplete": settings.grok_autocomplete_max_tokens
            }
        }
    }
