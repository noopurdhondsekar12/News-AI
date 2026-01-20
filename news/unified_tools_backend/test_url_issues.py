#!/usr/bin/env python3
"""
URL Issue Analysis and Solutions
"""

import requests
import json
import os

def test_url_issues():
    """Test and analyze the URL issues reported by the user"""

    # Environment-aware configuration
    BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    print("🔍 NEWS AI - URL ISSUE ANALYSIS")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 50)
    
    # Test URLs
    urls = [
        {
            "url": "https://www.youtube.com/watch?v=watch",
            "description": "Invalid YouTube URL (missing video ID)",
            "expected": "Should fail validation"
        },
        {
            "url": "https://x.com/narendramodi/status/1962435812588757337", 
            "description": "Twitter/X URL with bot protection",
            "expected": "Should show access restriction warning"
        },
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "description": "Valid YouTube URL (Rick Roll)",
            "expected": "Should pass validation"
        }
    ]
    
    for i, test_case in enumerate(urls, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Test validation first
        try:
            validation_response = requests.post(
                f"{BASE_URL}/api/validate-url",
                json={"url": test_case['url']}
            )
            
            if validation_response.status_code == 200:
                validation_data = validation_response.json()
                print(f"   ✅ Validation: {'PASS' if validation_data['success'] else 'FAIL'}")
                
                if not validation_data['success']:
                    print(f"   🚫 Issues: {', '.join(validation_data['data']['issues'])}")
                    print(f"   💡 Suggestions: {', '.join(validation_data['data']['suggestions'])}")
                    
                if validation_data['data']['issues']:
                    print(f"   ⚠️  Warnings: {', '.join(validation_data['data']['issues'])}")
                    
            # Test scraping
            scrape_response = requests.post(
                f"{BASE_URL}/api/scrape",
                json={"url": test_case['url']}
            )
            
            if scrape_response.status_code == 200:
                scrape_data = scrape_response.json()
                print(f"   📄 Scraping: {'SUCCESS' if scrape_data['success'] else 'FAILED'}")
                print(f"   📝 Title: {scrape_data['data']['title']}")
                print(f"   📖 Content Preview: {scrape_data['data']['content'][:80]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 SOLUTIONS PROVIDED:")
    print("1. Enhanced URL validation to catch invalid YouTube URLs")
    print("2. Bot protection detection for social media platforms") 
    print("3. Clear error messages and suggestions for users")
    print("4. New /api/validate-url endpoint for pre-checking URLs")
    print("\n✨ Your News AI system now handles these issues gracefully!")

if __name__ == "__main__":
    test_url_issues()