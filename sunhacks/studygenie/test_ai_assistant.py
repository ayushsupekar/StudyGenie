#!/usr/bin/env python3
"""
Test script for AI Assistant functionality
Run this to verify the AI assistant is working with the API key
"""

import os
import sys
import django
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

def test_environment():
    """Test if environment variables are loaded correctly"""
    print("=== Environment Test ===")
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    
    if api_key:
        print(f"[OK] GOOGLE_AI_API_KEY found: {api_key[:10]}...")
        return True
    else:
        print("[ERROR] GOOGLE_AI_API_KEY not found in environment")
        print("Make sure your .env file contains: GOOGLE_AI_API_KEY=your_actual_api_key")
        return False

def test_ai_services():
    """Test AI services initialization"""
    print("\n=== AI Services Test ===")
    try:
        from ai_services import client
        if client:
            print("[OK] AI client initialized successfully")
            return True
        else:
            print("[ERROR] AI client is None - check API key")
            return False
    except Exception as e:
        print(f"[ERROR] AI services error: {e}")
        return False

def test_ai_assistant():
    """Test the new AI assistant class"""
    print("\n=== AI Assistant Test ===")
    try:
        from dashboard.ai_assistant import ai_assistant
        
        # Test initialization
        if ai_assistant.model:
            print("[OK] AI Assistant initialized successfully")
        else:
            print("[WARNING] AI Assistant initialized but model is None")
        
        # Test response generation
        test_question = "What are good study techniques?"
        response = ai_assistant.generate_response(test_question)
        
        if response and len(response) > 50:
            print(f"[OK] AI response generated: {len(response)} characters")
            print(f"Sample: {response[:100]}...")
            return True
        else:
            print(f"[WARNING] AI response seems short: {response}")
            return False
            
    except Exception as e:
        print(f"[ERROR] AI Assistant error: {e}")
        return False

def test_fallback_responses():
    """Test fallback response system"""
    print("\n=== Fallback Response Test ===")
    try:
        from dashboard.ai_assistant import ai_assistant
        
        test_questions = [
            "Hello",
            "How to study effectively?",
            "Memory techniques",
            "Test preparation tips"
        ]
        
        for question in test_questions:
            response = ai_assistant.generate_fallback_response(question)
            if response and len(response) > 30:
                print(f"[OK] Fallback for '{question}': {len(response)} chars")
            else:
                print(f"[ERROR] Fallback failed for '{question}'")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Fallback test error: {e}")
        return False

def main():
    """Run all tests"""
    print("StudyGenie AI Assistant Test Suite")
    print("=" * 40)
    
    tests = [
        test_environment,
        test_ai_services, 
        test_ai_assistant,
        test_fallback_responses
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print(f"[PASSED] {sum(results)}/{len(results)}")
    print(f"[FAILED] {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n[SUCCESS] All tests passed! AI Assistant is ready to use.")
    else:
        print("\n[WARNING] Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure .env file exists with GOOGLE_AI_API_KEY")
        print("2. Install required packages: pip install -r requirements.txt")
        print("3. Check your Google AI API key is valid")

if __name__ == "__main__":
    main()