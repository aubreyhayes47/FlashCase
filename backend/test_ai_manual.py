#!/usr/bin/env python3
"""
Manual test script for AI endpoints.

This script demonstrates how to use the AI endpoints and verify
that streaming responses work correctly.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"


def test_ai_health():
    """Test AI health check endpoint."""
    print("=" * 60)
    print("Testing AI Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/ai/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_chat_no_stream():
    """Test chat endpoint without streaming."""
    print("=" * 60)
    print("Testing Chat (Non-Streaming)")
    print("=" * 60)
    
    payload = {
        "messages": [
            {"role": "user", "content": "What is jurisdiction in 5 words?"}
        ],
        "stream": False,
        "temperature": 0.5,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print()


def test_chat_with_stream():
    """Test chat endpoint with streaming."""
    print("=" * 60)
    print("Testing Chat (Streaming)")
    print("=" * 60)
    
    payload = {
        "messages": [
            {"role": "user", "content": "Explain Miranda rights briefly."}
        ],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/chat",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data = decoded[6:]
                        if data == "[DONE]":
                            print("\n[Stream ended]")
                            break
                        try:
                            chunk = json.loads(data)
                            if "content" in chunk:
                                print(chunk["content"], end="", flush=True)
                            elif "error" in chunk:
                                print(f"\nError: {chunk['error']}")
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print()


def test_rewrite_card():
    """Test card rewrite endpoint."""
    print("=" * 60)
    print("Testing Card Rewrite")
    print("=" * 60)
    
    payload = {
        "front": "What is jurisdiction?",
        "back": "Power of court to hear case",
        "instruction": "Make it more detailed and add citations"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/rewrite-card",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data = decoded[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "content" in chunk:
                                print(chunk["content"], end="", flush=True)
                                full_response += chunk["content"]
                        except json.JSONDecodeError:
                            pass
            print("\n")
            
            # Try to parse as JSON
            try:
                result = json.loads(full_response)
                print("Parsed result:")
                print(json.dumps(result, indent=2))
            except:
                pass
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print()


def test_autocomplete_card():
    """Test card autocomplete endpoint."""
    print("=" * 60)
    print("Testing Card Autocomplete")
    print("=" * 60)
    
    payload = {
        "partial_text": "What is the Fourth Amendment",
        "card_type": "front"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/autocomplete-card",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response:")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data = decoded[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "content" in chunk:
                                print(chunk["content"], end="", flush=True)
                                full_response += chunk["content"]
                        except json.JSONDecodeError:
                            pass
            print("\n")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print()


def main():
    """Run all manual tests."""
    print("\n" + "=" * 60)
    print("AI Endpoints Manual Test Suite")
    print("=" * 60)
    print("\nNote: These tests require the server to be running.")
    print("Start the server with: uvicorn app.main:app --reload")
    print("\nNote: Chat, rewrite, and autocomplete tests will fail")
    print("without valid GROK_API_KEY in .env file.\n")
    
    try:
        # Always test health check
        test_ai_health()
        
        # Test other endpoints (will show errors if API key not configured)
        test_chat_no_stream()
        test_chat_with_stream()
        test_rewrite_card()
        test_autocomplete_card()
        
        print("=" * 60)
        print("Manual tests completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
