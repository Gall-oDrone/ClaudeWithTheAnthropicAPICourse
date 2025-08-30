#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the evaluator fix works with the original code
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.anthropic_client import ChatClient
from utils.evaluator import Evaluator

def test_evaluator():
    """Test the evaluator with the original code structure"""
    
    # Initialize the chat client (you'll need to set your API key)
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your API key: export ANTHROPIC_API_KEY='your-key-here'")
        return False
    
    # Create chat client with default parameters
    chat_client = ChatClient(api_key=api_key, params={
        "max_tokens": 1000,
        "messages": [],
        "temperature": 0.7
    })
    
    # Create evaluator
    evaluator = Evaluator(chat_client)
    
    # Test with a simple dataset (same as your original code)
    test_dataset = [
        {"prompt": "Write a hello world function", "expected_response": "A function that prints hello world"},
        {"prompt": "What is 2+2?", "expected_response": "4"},  # Different field names
        {"prompt": "Explain Python lists", "expected_response": "Explanation of Python lists"}  # Yet different names
    ]
    
    print("🚀 Testing evaluator with JSON serialization fix...")
    
    try:
        # This should now work with the flexible evaluator
        results = evaluator.run_eval(test_dataset, save_results=False, verbose=True)
        print(f"✅ Success! Passed {results['passed_tests']}/{results['total_tests']} tests")
        
        # Test with save_results=True to verify JSON serialization
        print("\n🧪 Testing JSON serialization...")
        results_with_save = evaluator.run_eval(
            test_dataset[:1],  # Just one test case for speed
            save_results=True,
            results_path="test_eval_results.json",
            verbose=False
        )
        print("✅ JSON serialization successful!")
        
        # Clean up
        if os.path.exists("test_eval_results.json"):
            #os.remove("test_eval_results.json")
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_evaluator()
    sys.exit(0 if success else 1)
