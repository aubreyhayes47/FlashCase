#!/usr/bin/env python3
"""
Simple AI Token Usage Monitoring Script

This script polls the FlashCase API to monitor AI token usage in real-time.
It displays usage statistics and alerts when thresholds are exceeded.

Usage:
    python monitor_token_usage.py [--api-url URL] [--interval SECONDS]
    
Example:
    python monitor_token_usage.py --api-url http://localhost:8000/api/v1 --interval 60
"""

import argparse
import time
import sys
from datetime import datetime
from typing import Dict, Any
import httpx


def format_number(num: int) -> str:
    """Format number with thousands separator."""
    return f"{num:,}"


def print_banner():
    """Print monitoring banner."""
    print("=" * 80)
    print("FlashCase AI Token Usage Monitor".center(80))
    print("=" * 80)
    print()


def print_usage_stats(data: Dict[str, Any]) -> None:
    """Print formatted usage statistics."""
    usage = data.get("usage", {})
    alert_threshold = data.get("alert_threshold", 0)
    alert_triggered = data.get("alert_triggered", False)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n[{timestamp}]")
    print("-" * 80)
    
    # Token usage
    print(f"Total Tokens:         {format_number(usage.get('total_tokens', 0))}")
    print(f"  Prompt Tokens:      {format_number(usage.get('total_prompt_tokens', 0))}")
    print(f"  Completion Tokens:  {format_number(usage.get('total_completion_tokens', 0))}")
    print(f"Total Requests:       {format_number(usage.get('total_requests', 0))}")
    
    # Calculate progress to threshold
    total_tokens = usage.get('total_tokens', 0)
    if alert_threshold > 0:
        percentage = (total_tokens / alert_threshold) * 100
        progress_bar = create_progress_bar(percentage, width=40)
        print(f"\nThreshold Progress:   {progress_bar} {percentage:.1f}%")
        print(f"Alert Threshold:      {format_number(alert_threshold)} tokens")
    
    # Alert status
    if alert_triggered:
        print("\n⚠️  ALERT: Token usage threshold exceeded!")
    else:
        print("\n✓ Token usage within limits")
    
    # Cost control info
    cost_control = data.get("cost_control", {})
    if cost_control:
        print("\nCost Control Settings:")
        print(f"  Model:              {cost_control.get('model', 'N/A')}")
        print(f"  Temperature:        {cost_control.get('default_temperature', 'N/A')}")
        max_tokens = cost_control.get('max_tokens', {})
        if max_tokens:
            print(f"  Max Tokens:")
            print(f"    Chat:             {max_tokens.get('chat', 'N/A')}")
            print(f"    Rewrite:          {max_tokens.get('rewrite', 'N/A')}")
            print(f"    Autocomplete:     {max_tokens.get('autocomplete', 'N/A')}")
    
    # Rate limits
    rate_limits = data.get("rate_limits", {})
    if rate_limits:
        print("\nRate Limits:")
        print(f"  AI per minute:      {rate_limits.get('ai_per_minute', 'N/A')}")
        print(f"  AI per hour:        {rate_limits.get('ai_per_hour', 'N/A')}")
    
    print("-" * 80)


def create_progress_bar(percentage: float, width: int = 40) -> str:
    """Create a text-based progress bar."""
    filled = int((percentage / 100) * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}]"


def monitor_usage(api_url: str, interval: int, continuous: bool = True) -> None:
    """
    Monitor AI token usage by polling the API.
    
    Args:
        api_url: Base API URL
        interval: Polling interval in seconds
        continuous: Whether to run continuously or just once
    """
    usage_endpoint = f"{api_url}/ai/usage"
    
    print_banner()
    print(f"Monitoring endpoint: {usage_endpoint}")
    print(f"Polling interval:    {interval} seconds")
    print(f"Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(usage_endpoint)
                    response.raise_for_status()
                    data = response.json()
                    print_usage_stats(data)
                    
            except httpx.HTTPError as e:
                print(f"\n❌ Error fetching usage data: {e}", file=sys.stderr)
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
            
            if not continuous:
                break
            
            # Wait for next interval
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor FlashCase AI token usage in real-time"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="API base URL (default: http://localhost:8000/api/v1)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Polling interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't continuously monitor)"
    )
    
    args = parser.parse_args()
    
    monitor_usage(
        api_url=args.api_url,
        interval=args.interval,
        continuous=not args.once
    )


if __name__ == "__main__":
    main()
