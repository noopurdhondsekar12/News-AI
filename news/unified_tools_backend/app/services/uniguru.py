import httpx
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class UniguruService:
    def __init__(self):
        self.base_url = os.getenv("UNIGURU_BASE_URL", "https://api.uniguru.com")
        self.api_key = os.getenv("UNIGURU_API_KEY")
        self.timeout = 30.0

    async def classify_text(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Classify text content using Uniguru API"""
        try:
            if not self.api_key:
                return {"error": "Uniguru API key not configured"}

            url = f"{self.base_url}/classify"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": text[:5000],  # Limit text length
                "categories": categories or ["news", "sports", "politics", "technology", "entertainment"]
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "categories": result.get("categories", []),
                        "confidence_scores": result.get("confidence_scores", {}),
                        "primary_category": result.get("primary_category", ""),
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"Classification failed: {response.status_code}"}

        except Exception as e:
            return {"error": f"Uniguru classification error: {str(e)}"}

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using Uniguru API"""
        try:
            if not self.api_key:
                return {"error": "Uniguru API key not configured"}

            url = f"{self.base_url}/sentiment"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {"text": text[:5000]}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "sentiment": result.get("sentiment", "neutral"),
                        "polarity": result.get("polarity", 0.0),
                        "confidence": result.get("confidence", 0.0),
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"Sentiment analysis failed: {response.status_code}"}

        except Exception as e:
            return {"error": f"Uniguru sentiment error: {str(e)}"}

    async def summarize_text(self, text: str, max_length: int = 150, style: str = "concise") -> Dict[str, Any]:
        """Summarize text using Uniguru API"""
        try:
            if not self.api_key:
                return {"error": "Uniguru API key not configured"}

            url = f"{self.base_url}/summarize"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": text[:10000],  # Limit text length
                "max_length": max_length,
                "style": style
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "summary": result.get("summary", ""),
                        "original_length": len(text),
                        "summary_length": len(result.get("summary", "")),
                        "compression_ratio": len(result.get("summary", "")) / len(text) if text else 0,
                        "processed_at": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"Summarization failed: {response.status_code}"}

        except Exception as e:
            return {"error": f"Uniguru summarization error: {str(e)}"}

# Global instance
uniguru_service = UniguruService()