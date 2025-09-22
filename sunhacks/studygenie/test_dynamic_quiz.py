#!/usr/bin/env python
"""
Test dynamic quiz generation with different difficulty levels
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_quiz_with_ai

def test_dynamic_quiz():
    """Test dynamic quiz generation for all difficulty levels"""
    
    # Get a document to test
    doc = Document.objects.filter(extracted_text__isnull=False).exclude(extracted_text='').first()
    
    if not doc:
        print("No documents found")
        return
    
    print(f"Testing dynamic quiz generation for: {doc.title}")
    print("="*60)
    
    # Test all difficulty levels
    difficulties = ['easy', 'medium', 'hard']
    
    for difficulty in difficulties:
        print(f"\\n{difficulty.upper()} LEVEL QUIZ")
        print("-"*30)
        
        # Use both summary and extracted text for better content
        content = f"{doc.summary}\\n\\n{doc.extracted_text[:2000]}" if doc.summary else doc.extracted_text
        
        quiz_questions = generate_quiz_with_ai(content, difficulty=difficulty)
        
        print(f"Generated {len(quiz_questions)} questions")
        
        # Show first 3 questions as examples
        for i, q in enumerate(quiz_questions[:3], 1):
            print(f"\\nQ{i}: {q['stem']}")
            for option_key, option_text in q['options'].items():
                marker = "✓" if option_key == q['answer_key'] else " "
                print(f"  {marker} {option_key}) {option_text}")
            print(f"   Explanation: {q['explanation']}")
            if 'topic' in q:
                print(f"   Topic: {q['topic']}")
        
        if len(quiz_questions) > 3:
            print(f"\\n... and {len(quiz_questions) - 3} more questions")

if __name__ == "__main__":
    test_dynamic_quiz()