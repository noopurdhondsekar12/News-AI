#!/usr/bin/env python3
"""
Light Load Test for News AI Backend
Runs multiple concurrent requests to test system performance
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_URLS = [
    "https://www.bbc.com/news",
    "https://www.reuters.com/",
    "https://www.nytimes.com/",
    "https://www.theguardian.com/international",
    "https://www.aljazeera.com/"
]

CONCURRENT_REQUESTS = 3  # Light load
REQUESTS_PER_URL = 2

async def single_request(client: httpx.AsyncClient, url: str, request_id: int) -> Dict[str, Any]:
    """Make a single request and return results"""
    start_time = time.time()
    try:
        data = {
            "url": url,
            "options": {
                "enable_bhiv_push": False,  # Disable for testing
                "enable_audio": False,
                "channels": ["test_channel"],
                "avatars": ["test_avatar"]
            }
        }

        response = await client.post(f"{BASE_URL}/api/process-news", json=data, timeout=120.0)
        latency = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            return {
                "request_id": request_id,
                "url": url,
                "success": True,
                "latency": latency,
                "status_code": response.status_code,
                "response_size": len(json.dumps(result))
            }
        else:
            return {
                "request_id": request_id,
                "url": url,
                "success": False,
                "latency": latency,
                "status_code": response.status_code,
                "error": response.text[:200]  # Truncate error
            }

    except Exception as e:
        latency = time.time() - start_time
        return {
            "request_id": request_id,
            "url": url,
            "success": False,
            "latency": latency,
            "error": str(e)
        }

async def run_load_test():
    """Run the load test"""
    print("🚀 Starting Light Load Test for News AI Backend")
    print(f"Concurrent requests: {CONCURRENT_REQUESTS}")
    print(f"Requests per URL: {REQUESTS_PER_URL}")
    print(f"Total URLs: {len(TEST_URLS)}")
    print("=" * 60)

    results = []
    request_id = 0

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

        async def limited_request(url: str):
            async with semaphore:
                nonlocal request_id
                req_id = request_id
                request_id += 1
                return await single_request(client, url, req_id)

        # Generate all requests
        tasks = []
        for url in TEST_URLS:
            for _ in range(REQUESTS_PER_URL):
                tasks.append(limited_request(url))

        # Run all tasks concurrently with semaphore
        start_time = time.time()
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Process results
        successful = 0
        failed = 0
        total_latency = 0

        for result in completed_results:
            if isinstance(result, Exception):
                print(f"❌ Task failed with exception: {result}")
                failed += 1
                results.append({
                    "request_id": -1,
                    "success": False,
                    "error": str(result)
                })
            else:
                results.append(result)
                if result["success"]:
                    successful += 1
                    total_latency += result["latency"]
                else:
                    failed += 1

        # Calculate metrics
        avg_latency = total_latency / successful if successful > 0 else 0
        throughput = len(tasks) / total_time

        # Print summary
        print("\n📊 Load Test Results:")
        print(f"Total requests: {len(tasks)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Average latency: {avg_latency:.2f}s")
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {throughput:.2f} req/s")
        # Save results
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_config": {
                "concurrent_requests": CONCURRENT_REQUESTS,
                "requests_per_url": REQUESTS_PER_URL,
                "total_urls": len(TEST_URLS),
                "base_url": BASE_URL
            },
            "performance_metrics": {
                "total_requests": len(tasks),
                "successful_requests": successful,
                "failed_requests": failed,
                "total_time_seconds": total_time,
                "average_latency_seconds": avg_latency,
                "throughput_requests_per_second": throughput
            },
            "individual_results": results
        }

        with open("load_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)

        print(f"\n💾 Results saved to load_test_results.json")

        return test_results

if __name__ == "__main__":
    asyncio.run(run_load_test())