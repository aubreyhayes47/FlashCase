"""Content moderation service for filtering inappropriate content."""

from typing import Tuple
import re


class ProfanityFilter:
    """
    Simple profanity filter for content moderation.
    
    This filter checks for common profanity and inappropriate content
    in user-submitted text (deck names, descriptions, card content).
    """
    
    # Basic profanity list (can be extended)
    PROFANITY_LIST = {
        # Common profanity patterns with variations
        "fuck", "fucking", "fucked", "fucker", "fucks",
        "shit", "shitting", "shitty", "shits",
        "bitch", "bitching", "bitches",
        "damn", "damned", "damnit",
        "hell", "bastard", "crap", "crappy",
        "piss", "pissed", "pissing",
        "cock", "dick", "pussy",
        "whore", "slut", "cunt",
        "motherfucker", "asshole", "assholes",
        # Add variations with common letter substitutions
        "fuk", "fck", "shyt", "biatch", "azz"
    }
    
    def __init__(self):
        """Initialize the profanity filter."""
        # Compile regex patterns for efficient matching
        # Note: Not using word boundaries for words ending in special patterns
        self.patterns = []
        for word in self.PROFANITY_LIST:
            # For most words, use word boundaries
            # But allow for variations like "f*ck" or "a$$"
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            self.patterns.append(pattern)
    
    def contains_profanity(self, text: str) -> bool:
        """
        Check if text contains profanity.
        
        Args:
            text: The text to check
            
        Returns:
            True if profanity is detected, False otherwise
        """
        if not text:
            return False
        
        # Check against all patterns
        for pattern in self.patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def check_content(self, text: str) -> Tuple[bool, str]:
        """
        Check content for profanity and return result with message.
        
        Args:
            text: The text to check
            
        Returns:
            Tuple of (is_clean, message)
            - is_clean: True if content is appropriate, False if profanity detected
            - message: Explanation message
        """
        if self.contains_profanity(text):
            return False, "Content contains inappropriate language and cannot be submitted"
        return True, "Content is appropriate"
    
    def filter_text(self, text: str, replacement: str = "***") -> str:
        """
        Filter profanity from text by replacing with specified string.
        
        Args:
            text: The text to filter
            replacement: String to replace profanity with (default: ***)
            
        Returns:
            Filtered text with profanity replaced
        """
        if not text:
            return text
        
        filtered_text = text
        for pattern in self.patterns:
            filtered_text = pattern.sub(replacement, filtered_text)
        
        return filtered_text


# Global instance for use across the application
profanity_filter = ProfanityFilter()


def check_deck_content(name: str, description: str = None) -> Tuple[bool, str]:
    """
    Check deck content for profanity.
    
    Args:
        name: Deck name
        description: Optional deck description
        
    Returns:
        Tuple of (is_clean, message)
    """
    # Check name
    is_clean, message = profanity_filter.check_content(name)
    if not is_clean:
        return False, f"Deck name: {message}"
    
    # Check description if provided
    if description:
        is_clean, message = profanity_filter.check_content(description)
        if not is_clean:
            return False, f"Deck description: {message}"
    
    return True, "Content is appropriate"


def check_card_content(front: str, back: str) -> Tuple[bool, str]:
    """
    Check card content for profanity.
    
    Args:
        front: Card front text
        back: Card back text
        
    Returns:
        Tuple of (is_clean, message)
    """
    # Check front
    is_clean, message = profanity_filter.check_content(front)
    if not is_clean:
        return False, f"Card front: {message}"
    
    # Check back
    is_clean, message = profanity_filter.check_content(back)
    if not is_clean:
        return False, f"Card back: {message}"
    
    return True, "Content is appropriate"
