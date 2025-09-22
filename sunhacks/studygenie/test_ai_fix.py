#!/usr/bin/env python
"""
Test script to verify AI services are working
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

# Test AI services
def test_ai_services():
    print("Testing AI Services...")
    
    try:
        from ai_services import generate_summary_with_ai, generate_quiz_with_ai, generate_flashcards_with_ai
        
        # Test text
        test_text = """
        Machine learning is a subset of artificial intelligence that focuses on algorithms 
        that can learn from data. It involves training models on datasets to make predictions 
        or decisions without being explicitly programmed for every scenario.
        """
        
        print("\n1. Testing Summary Generation...")
        summary = generate_summary_with_ai(test_text)
        print(f"Summary: {summary[:100]}...")
        
        print("\n2. Testing Quiz Generation...")
        quiz = generate_quiz_with_ai(test_text)
        print(f"Generated {len(quiz)} quiz questions")
        
        print("\n3. Testing Flashcard Generation...")
        flashcards = generate_flashcards_with_ai(test_text)
        print(f"Generated {len(flashcards)} flashcards")
        
        print("\n✅ All AI services are working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI services: {e}")
        return False

if __name__ == "__main__":
    test_ai_services()