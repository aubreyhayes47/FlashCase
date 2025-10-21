"""Content moderation service for filtering inappropriate content."""

from better_profanity import profanity
from typing import Tuple


# Initialize profanity filter
profanity.load_censor_words()


def is_content_appropriate(text: str) -> Tuple[bool, str]:
    """
    Check if text content is appropriate (no profanity).
    
    Args:
        text: The text to check
        
    Returns:
        Tuple of (is_appropriate, reason)
        - is_appropriate: True if content is appropriate, False otherwise
        - reason: Empty string if appropriate, error message otherwise
    """
    if not text or not text.strip():
        return True, ""
    
    if profanity.contains_profanity(text):
        return False, "Content contains inappropriate language"
    
    return True, ""


def censor_text(text: str) -> str:
    """
    Censor profanity in text.
    
    Args:
        text: The text to censor
        
    Returns:
        Censored text with profanity replaced by asterisks
    """
    if not text:
        return text
    
    return profanity.censor(text)


def validate_deck_content(name: str, description: str = None) -> Tuple[bool, str]:
    """
    Validate deck content for appropriateness.
    
    Args:
        name: Deck name
        description: Optional deck description
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check name
    is_appropriate, reason = is_content_appropriate(name)
    if not is_appropriate:
        return False, f"Deck name: {reason}"
    
    # Check description if provided
    if description:
        is_appropriate, reason = is_content_appropriate(description)
        if not is_appropriate:
            return False, f"Deck description: {reason}"
    
    return True, ""


def validate_card_content(front: str, back: str) -> Tuple[bool, str]:
    """
    Validate card content for appropriateness.
    
    Args:
        front: Card front text
        back: Card back text
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check front
    is_appropriate, reason = is_content_appropriate(front)
    if not is_appropriate:
        return False, f"Card front: {reason}"
    
    # Check back
    is_appropriate, reason = is_content_appropriate(back)
    if not is_appropriate:
        return False, f"Card back: {reason}"
    
    return True, ""
