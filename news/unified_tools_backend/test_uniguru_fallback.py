#!/usr/bin/env python3
"""
Test script to validate Uniguru fallback behavior
"""

import asyncio
import os
from app.services.uniguru import UniguruService

async def test_uniguru_fallback():
    """Test Uniguru fallback mechanisms"""
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    print("🧪 Testing Uniguru Fallback Behavior")
    print(f"Environment: {ENVIRONMENT}")
    print("=" * 50)

    # Create service instance
    service = UniguruService()

    # Test data
    test_text = "This is a sample news article about technology and artificial intelligence. It discusses recent developments in AI research."

    # Test 1: Normal operation (if API key exists)
    print("\n1. Testing normal operation...")
    try:
        result = await service.classify_text(test_text)
        has_fallback = result.get("fallback_used", False)
        print(f"   Classification result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        print(f"   Fallback used: {has_fallback}")
        if result.get('success'):
            print(f"   Primary category: {result.get('primary_category', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Force fallback by removing API key temporarily
    print("\n2. Testing forced fallback (no API key)...")
    original_key = service.api_key
    service.api_key = None  # Force fallback

    try:
        result = await service.classify_text(test_text)
        has_fallback = result.get("fallback_used", False)
        print(f"   Classification result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        print(f"   Fallback used: {has_fallback}")
        if result.get('success'):
            print(f"   Primary category: {result.get('primary_category', 'N/A')}")
            print(f"   Categories: {result.get('categories', [])}")
    except Exception as e:
        print(f"   Error: {e}")
    finally:
        service.api_key = original_key  # Restore

    # Test 3: Sentiment analysis fallback
    print("\n3. Testing sentiment analysis fallback...")
    service.api_key = None  # Force fallback

    try:
        result = await service.analyze_sentiment(test_text)
        has_fallback = result.get("fallback_used", False)
        print(f"   Sentiment result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        print(f"   Fallback used: {has_fallback}")
        if result.get('success'):
            print(f"   Sentiment: {result.get('sentiment', 'N/A')}")
            print(f"   Polarity: {result.get('polarity', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    finally:
        service.api_key = original_key

    # Test 4: Summarization fallback
    print("\n4. Testing summarization fallback...")
    service.api_key = None  # Force fallback

    try:
        result = await service.summarize_text(test_text, max_length=100)
        has_fallback = result.get("fallback_used", False)
        print(f"   Summarization result: {'✅ Success' if result.get('success') else '❌ Failed'}")
        print(f"   Fallback used: {has_fallback}")
        if result.get('success'):
            print(f"   Summary: {result.get('summary', 'N/A')[:100]}...")
            print(f"   Compression ratio: {result.get('compression_ratio', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    finally:
        service.api_key = original_key

    print("\n🎯 Fallback Validation Complete")
    print("Expected behavior: All fallback tests should succeed with 'fallback_used': true")

if __name__ == "__main__":
    asyncio.run(test_uniguru_fallback())