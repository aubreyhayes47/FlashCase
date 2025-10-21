"""Tests for the SM-2 spaced repetition algorithm."""

import pytest
from datetime import datetime, timedelta
from app.services.srs import calculate_sm2, calculate_due_date


class TestCalculateSM2:
    """Test cases for the SM-2 algorithm implementation."""
    
    def test_perfect_response_first_repetition(self):
        """Test perfect response (quality 5) on first repetition."""
        repetitions = 0
        ease_factor = 2.5
        interval = 0
        quality = 5
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 1
        assert new_interval == 1  # First repetition: 1 day
        assert new_ef > ease_factor  # EF should increase with perfect response
    
    def test_perfect_response_second_repetition(self):
        """Test perfect response (quality 5) on second repetition."""
        repetitions = 1
        ease_factor = 2.6
        interval = 1
        quality = 5
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 2
        assert new_interval == 6  # Second repetition: 6 days
        assert new_ef >= ease_factor  # EF should increase or stay same
    
    def test_perfect_response_third_repetition(self):
        """Test perfect response (quality 5) on third+ repetition."""
        repetitions = 2
        ease_factor = 2.6
        interval = 6
        quality = 5
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 3
        assert new_interval == int(round(interval * new_ef))  # Multiply by EF
        assert new_ef >= ease_factor
    
    def test_correct_response_with_hesitation(self):
        """Test correct but hesitant response (quality 4)."""
        repetitions = 1
        ease_factor = 2.5
        interval = 1
        quality = 4
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 2
        assert new_interval == 6
        # EF should be relatively unchanged or slightly increased
        assert new_ef >= 2.4
    
    def test_correct_with_difficulty(self):
        """Test correct response with difficulty (quality 3)."""
        repetitions = 2
        ease_factor = 2.5
        interval = 6
        quality = 3
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 3  # Still correct, increment
        # EF should decrease but respect floor of 1.3
        assert new_ef >= 1.3
        assert new_ef < ease_factor  # Should decrease
    
    def test_incorrect_response_resets_repetitions(self):
        """Test that incorrect response (quality < 3) resets repetitions."""
        repetitions = 5
        ease_factor = 2.3
        interval = 30
        quality = 2  # Incorrect
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 0  # Reset to 0
        assert new_interval == 1  # Start over with 1 day
        assert new_ef >= 1.3  # Should still respect floor
    
    def test_complete_blackout(self):
        """Test complete blackout (quality 0)."""
        repetitions = 3
        ease_factor = 2.5
        interval = 15
        quality = 0
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_reps == 0
        assert new_interval == 1
        # EF should decrease significantly but respect floor
        assert new_ef >= 1.3
    
    def test_ease_factor_floor(self):
        """Test that ease factor never goes below 1.3 (ease-hell mitigation)."""
        repetitions = 1
        ease_factor = 1.4  # Close to floor
        interval = 1
        quality = 0  # Worst rating
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        assert new_ef >= 1.3  # Should never go below floor
    
    def test_ease_factor_floor_enforced_on_input(self):
        """Test that ease factor floor is enforced even if input is below 1.3."""
        repetitions = 1
        ease_factor = 1.0  # Below floor
        interval = 1
        quality = 5
        
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, ease_factor, interval
        )
        
        # Should use 1.3 as base, not 1.0
        assert new_ef >= 1.3
    
    def test_invalid_quality_raises_error(self):
        """Test that invalid quality values raise ValueError."""
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            calculate_sm2(quality=6, repetitions=0, ease_factor=2.5, interval=0)
        
        with pytest.raises(ValueError, match="Quality must be between 0 and 5"):
            calculate_sm2(quality=-1, repetitions=0, ease_factor=2.5, interval=0)
    
    def test_progression_sequence(self):
        """Test a realistic progression sequence."""
        # Start with new card
        repetitions = 0
        ease_factor = 2.5
        interval = 0
        
        # First review: quality 5 (perfect)
        repetitions, ease_factor, interval = calculate_sm2(5, repetitions, ease_factor, interval)
        assert repetitions == 1
        assert interval == 1
        
        # Second review: quality 5 (perfect)
        repetitions, ease_factor, interval = calculate_sm2(5, repetitions, ease_factor, interval)
        assert repetitions == 2
        assert interval == 6
        
        # Third review: quality 4 (good)
        repetitions, ease_factor, interval = calculate_sm2(4, repetitions, ease_factor, interval)
        assert repetitions == 3
        assert interval > 6  # Should be longer
        
        # Fourth review: quality 2 (forgot)
        repetitions, ease_factor, interval = calculate_sm2(2, repetitions, ease_factor, interval)
        assert repetitions == 0  # Reset
        assert interval == 1  # Back to start


class TestCalculateDueDate:
    """Test cases for due date calculation."""
    
    def test_calculate_due_date_from_now(self):
        """Test calculating due date from current time."""
        interval = 5
        before = datetime.utcnow()
        due_date = calculate_due_date(interval)
        after = datetime.utcnow()
        
        # Due date should be approximately 5 days from now
        expected_min = before + timedelta(days=5)
        expected_max = after + timedelta(days=5)
        
        assert expected_min <= due_date <= expected_max
    
    def test_calculate_due_date_from_base_date(self):
        """Test calculating due date from a specific base date."""
        base_date = datetime(2025, 1, 1, 12, 0, 0)
        interval = 10
        
        due_date = calculate_due_date(interval, base_date)
        
        expected = datetime(2025, 1, 11, 12, 0, 0)
        assert due_date == expected
    
    def test_calculate_due_date_zero_interval(self):
        """Test calculating due date with zero interval."""
        base_date = datetime(2025, 1, 1, 12, 0, 0)
        interval = 0
        
        due_date = calculate_due_date(interval, base_date)
        
        # Should be same as base date
        assert due_date == base_date
    
    def test_calculate_due_date_large_interval(self):
        """Test calculating due date with large interval."""
        base_date = datetime(2025, 1, 1)
        interval = 365  # One year
        
        due_date = calculate_due_date(interval, base_date)
        
        expected = datetime(2026, 1, 1)
        assert due_date == expected
