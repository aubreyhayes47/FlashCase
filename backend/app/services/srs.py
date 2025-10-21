"""
Spaced Repetition System (SRS) service using modified SM-2 algorithm.

This implementation is based on the SuperMemo SM-2 algorithm with Anki improvements:
- EF floor of 1.3 (instead of 1.2) to prevent ease-hell
- Initial learning steps for new cards
- Modified intervals for better retention

Reference: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""

from datetime import datetime, timedelta
from typing import Tuple


def calculate_sm2(
    quality: int,
    repetitions: int,
    ease_factor: float,
    interval: int
) -> Tuple[int, float, int]:
    """
    Calculate the next review parameters using the modified SM-2 algorithm.
    
    Args:
        quality: Quality of recall (0-5)
            0 - Complete blackout
            1 - Incorrect response; correct one remembered
            2 - Incorrect response; correct one seemed easy to recall
            3 - Correct response recalled with serious difficulty
            4 - Correct response after hesitation
            5 - Perfect response
        repetitions: Number of consecutive correct repetitions
        ease_factor: Current ease factor (EF), should be >= 1.3
        interval: Current interval in days
        
    Returns:
        Tuple of (new_repetitions, new_ease_factor, new_interval)
        
    Algorithm:
        - If quality < 3: Reset repetitions to 0, interval resets to initial learning
        - If quality >= 3:
            - Increment repetitions
            - Update ease factor with floor of 1.3 (ease-hell mitigation)
            - Calculate new interval based on repetitions:
                - First repetition: 1 day
                - Second repetition: 6 days
                - Subsequent: interval * ease_factor
    """
    # Validate inputs
    if not 0 <= quality <= 5:
        raise ValueError("Quality must be between 0 and 5")
    
    if ease_factor < 1.3:
        ease_factor = 1.3
    
    # Calculate new ease factor
    # SM-2 formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # Apply ease floor of 1.3 to prevent ease-hell
    if new_ease_factor < 1.3:
        new_ease_factor = 1.3
    
    # Check if response was correct (quality >= 3)
    if quality < 3:
        # Incorrect response - reset repetitions and start over
        new_repetitions = 0
        new_interval = 1  # Start with 1 day for relearning
    else:
        # Correct response - continue with spaced repetition
        new_repetitions = repetitions + 1
        
        # Calculate interval based on repetitions
        if new_repetitions == 1:
            # First correct repetition: 1 day
            new_interval = 1
        elif new_repetitions == 2:
            # Second correct repetition: 6 days
            new_interval = 6
        else:
            # Subsequent repetitions: multiply by ease factor
            new_interval = int(round(interval * new_ease_factor))
    
    return new_repetitions, new_ease_factor, new_interval


def calculate_due_date(interval: int, base_date: datetime = None) -> datetime:
    """
    Calculate the due date based on the interval.
    
    Args:
        interval: Number of days until the card is due
        base_date: Base date to calculate from (defaults to now)
        
    Returns:
        datetime: The due date
    """
    if base_date is None:
        base_date = datetime.utcnow()
    
    return base_date + timedelta(days=interval)
