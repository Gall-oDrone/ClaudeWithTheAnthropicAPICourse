#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify JSON serialization of GradingResult objects
"""

import json
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.graders import GradingResult, Grader
from utils.evaluator import GradingResultEncoder

def test_json_serialization():
    """Test that GradingResult objects can be serialized to JSON"""
    
    # Create a sample GradingResult
    grading_result = GradingResult(
        score=8.5,
        feedback="Good response with minor issues",
        details={"length": 150, "readability": 7.5},
        passed=True
    )
    
    # Test direct serialization
    try:
        json_str = json.dumps(grading_result, cls=GradingResultEncoder, indent=2)
        print("✅ Direct JSON serialization successful!")
        print(json_str)
    except Exception as e:
        print(f"❌ Direct JSON serialization failed: {e}")
        return False
    
    # Test serialization in a dictionary
    test_data = {
        "test_name": "Sample Test",
        "result": grading_result,
        "metadata": {"timestamp": "2024-01-01"}
    }
    
    try:
        json_str = json.dumps(test_data, cls=GradingResultEncoder, indent=2)
        print("\n✅ Dictionary JSON serialization successful!")
        print(json_str)
    except Exception as e:
        print(f"❌ Dictionary JSON serialization failed: {e}")
        return False
    
    # Test file serialization
    try:
        with open("test_results.json", "w") as f:
            json.dump(test_data, f, cls=GradingResultEncoder, indent=2)
        print("\n✅ File JSON serialization successful!")
        
        # Clean up
        os.remove("test_results.json")
    except Exception as e:
        print(f"❌ File JSON serialization failed: {e}")
        return False
    
    print("\n🎉 All JSON serialization tests passed!")
    return True

if __name__ == "__main__":
    success = test_json_serialization()
    sys.exit(0 if success else 1)
