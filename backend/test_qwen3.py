#!/usr/bin/env python3
"""
Test script for Qwen3 (Free-QWQ) API integration
Tests the AI service with Qwen3 API
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.ai_service import AIService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_qwen3_basic():
    """Test basic Qwen3 API connection"""
    print("=" * 60)
    print("Testing Qwen3 (Free-QWQ) API Integration")
    print("=" * 60)
    
    api_key = os.getenv('QWEN3_API_KEY')
    api_endpoint = os.getenv('QWEN3_API_ENDPOINT', 'https://api.suanli.cn/v1')
    model = os.getenv('AI_MODEL', 'free:QwQ-32B')
    
    print(f"\n[INFO] API Configuration:")
    print(f"  Provider: qwen3")
    print(f"  Model: {model}")
    print(f"  Endpoint: {api_endpoint}")
    print(f"  API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT SET'}")
    
    if not api_key:
        print("\n[ERROR] QWEN3_API_KEY not set in environment!")
        return False
    
    try:
        print("\n[INFO] Initializing Qwen3 AI Service...")
        service = AIService(
            api_key=api_key,
            model=model,
            provider='qwen3',
            api_endpoint=api_endpoint
        )
        print("[✓] AI Service initialized successfully")
        
        # Test simple prompt
        print("\n[INFO] Testing simple API call...")
        test_prompt = "请用一句话用中文解释什么是机器学习。"
        response = service._generate_content(test_prompt)
        
        if response:
            print(f"[✓] API call successful!")
            print(f"[Response]\n{response}\n")
            return True
        else:
            print("[✗] API call returned empty response")
            return False
            
    except Exception as e:
        print(f"[✗] Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paper_summarization():
    """Test paper summarization with Qwen3"""
    print("\n" + "=" * 60)
    print("Testing Paper Summarization")
    print("=" * 60)
    
    api_key = os.getenv('QWEN3_API_KEY')
    api_endpoint = os.getenv('QWEN3_API_ENDPOINT', 'https://api.suanli.cn/v1')
    model = os.getenv('AI_MODEL', 'free:QwQ-32B')
    
    try:
        service = AIService(
            api_key=api_key,
            model=model,
            provider='qwen3',
            api_endpoint=api_endpoint
        )
        
        test_paper = {
            'title': 'Attention Is All You Need',
            'summary': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks'
        }
        
        print(f"\n[INFO] Testing paper summarization...")
        print(f"  Title: {test_paper['title']}")
        summary = service.summarize_paper(
            test_paper['title'],
            test_paper['summary'],
            max_length=150
        )
        
        if summary:
            print(f"[✓] Paper summarization successful!")
            print(f"[Summary]\n{summary}\n")
            return True
        else:
            print("[✗] Summarization returned empty response")
            return False
            
    except Exception as e:
        print(f"[✗] Error during summarization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n🧪 Qwen3 API Integration Test Suite\n")
    
    test1 = test_qwen3_basic()
    test2 = test_paper_summarization()
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Basic API Test: {'✓ PASSED' if test1 else '✗ FAILED'}")
    print(f"Paper Summarization: {'✓ PASSED' if test2 else '✗ FAILED'}")
    
    if test1 and test2:
        print("\n✓ All tests passed! Qwen3 integration is working correctly.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please check the configuration.")
        sys.exit(1)
