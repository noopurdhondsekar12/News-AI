#!/usr/bin/env python3
"""
Test Blackhole LLM Integration
"""

import requests
import json
import os

def test_blackhole_llm():
    """Test the Blackhole LLM configuration"""

    # Environment-aware configuration
    BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    print("🧪 Testing Blackhole LLM Integration")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend Health Check:")
            print(f"   Status: {health_data['status']}")
            print(f"   Summarizing via: {health_data['services']['summarizing_via']}")
            print(f"   Blackhole LLM: {health_data['services']['blackhole_llm']}")
            print(f"   Blackhole URL: {health_data['services']['blackhole_llm_url']}")
            print(f"   Blackhole Model: {health_data['services'].get('blackhole_llm_model', 'Not specified')}")
            
            # Test summarization with Blackhole LLM
            print("\n🤖 Testing Summarization with Blackhole LLM:")
            test_text = """
            Artificial Intelligence is revolutionizing the way we process information. 
            Machine learning algorithms can analyze vast amounts of data to identify patterns 
            and make predictions. This technology has applications in healthcare, finance, 
            transportation, and many other industries. As AI continues to evolve, it promises 
            to transform how we work and live.
            """
            
            summarize_response = requests.post(
                f"{BASE_URL}/api/summarize",
                json={
                    "text": test_text,
                    "max_length": 100,
                    "style": "concise"
                }
            )
            
            if summarize_response.status_code == 200:
                summary_data = summarize_response.json()
                print("✅ Summarization Test Successful:")
                print(f"   Summary: {summary_data['data']['summary']}")
                print(f"   Model: {summary_data['data']['model']}")
                print(f"   Endpoint: {summary_data['data'].get('endpoint', 'N/A')}")
                return True
            else:
                print(f"❌ Summarization failed: {summarize_response.status_code}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_blackhole_llm()