#!/usr/bin/env python
"""
Test the improved paragraph summary format with introduction, concepts, and closing
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import generate_summary_with_ai, generate_quiz_with_ai

def test_paragraph_summary():
    """Test paragraph format summary with three parts"""
    
    sample_text = """
    Control statements in programming are fundamental constructs that control the flow of execution in a program. 
    Control statements allow programmers to make decisions and repeat actions based on certain conditions.
    
    There are three main types of control statements:
    1. Conditional statements (if, if-else, switch)
    2. Looping statements (for, while, do-while)  
    3. Jump statements (break, continue, return)
    
    Conditional statements execute different code blocks based on conditions.
    Looping statements repeat code blocks multiple times.
    Jump statements alter the normal flow of execution.
    """
    
    print("=== TESTING PARAGRAPH SUMMARY FORMAT ===\n")
    
    try:
        summary = generate_summary_with_ai(sample_text)
        print("Generated Summary:")
        print("-" * 50)
        print(summary)
        print(f"\nLength: {len(summary)} characters")
        print(f"Words: {len(summary.split())} words")
        
        # Check if it's in paragraph format
        if '\n' not in summary.strip() or summary.count('\n') <= 2:
            print("✓ Paragraph format confirmed")
        else:
            print("⚠ Not in single paragraph format")
            
    except Exception as e:
        print(f"Error: {e}")

def test_unique_quiz_questions():
    """Test that different difficulty levels generate different questions"""
    
    sample_text = """
    Object-oriented programming (OOP) is a programming paradigm based on objects and classes.
    Key concepts include encapsulation, inheritance, and polymorphism.
    Encapsulation bundles data and methods together.
    Inheritance allows classes to inherit properties from other classes.
    Polymorphism enables objects to take multiple forms.
    """
    
    print("\n=== TESTING UNIQUE QUIZ QUESTIONS ===\n")
    
    difficulties = ['easy', 'medium', 'hard']
    all_questions = {}
    
    for difficulty in difficulties:
        try:
            questions = generate_quiz_with_ai(sample_text, difficulty)
            all_questions[difficulty] = questions
            print(f"{difficulty.upper()} Questions:")
            print("-" * 30)
            for i, q in enumerate(questions[:3], 1):  # Show first 3
                print(f"{i}. {q['stem']}")
            print()
        except Exception as e:
            print(f"Error generating {difficulty} questions: {e}")
    
    # Check for uniqueness
    easy_stems = [q['stem'] for q in all_questions.get('easy', [])]
    medium_stems = [q['stem'] for q in all_questions.get('medium', [])]
    hard_stems = [q['stem'] for q in all_questions.get('hard', [])]
    
    easy_medium_overlap = set(easy_stems) & set(medium_stems)
    medium_hard_overlap = set(medium_stems) & set(hard_stems)
    easy_hard_overlap = set(easy_stems) & set(hard_stems)
    
    print("UNIQUENESS CHECK:")
    print(f"Easy-Medium overlap: {len(easy_medium_overlap)} questions")
    print(f"Medium-Hard overlap: {len(medium_hard_overlap)} questions")
    print(f"Easy-Hard overlap: {len(easy_hard_overlap)} questions")
    
    if not any([easy_medium_overlap, medium_hard_overlap, easy_hard_overlap]):
        print("✓ All difficulty levels have unique questions")
    else:
        print("⚠ Some questions overlap between difficulty levels")

if __name__ == "__main__":
    test_paragraph_summary()
    test_unique_quiz_questions()