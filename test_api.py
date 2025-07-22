#!/usr/bin/env python3
"""
Test script for Document Search API
"""
import requests
import json


def test_api():
    base_url = "http://localhost:8001"
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test search endpoint
    print("🔍 Testing search endpoint...")
    test_queries = [
        "self attention",
        "transformer model",
        "attention mechanism"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        try:
            payload = {"query": query}
            response = requests.post(
                f"{base_url}/search-files",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Query: {result['query']}")
                print(f"Found {len(result['results'])} file_id results:")
                
                for i, res in enumerate(result['results'], 1):
                    print(f"  {i}. File ID: {res['file_id']}")
                    print(f"     Score: {res['score']}")
                    print(f"     Content: {res['content'][:100]}...")
                    print()
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure the API is running on localhost:8001")
    print("Run: uvicorn app:app --reload --port 8001")
    print("=" * 50)
    
    test_api()
