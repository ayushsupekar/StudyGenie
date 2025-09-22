#!/usr/bin/env python
"""
Test script for improved AI summary generation
Tests brief, comprehensive summaries without redundancy
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import generate_summary_with_ai, generate_smart_fallback_summary

def test_summary_improvements():
    """Test the improved summary generation"""
    
    # Sample educational text with potential redundancy
    sample_text = """
    Control statements in programming are fundamental constructs that control the flow of execution in a program. 
    Control statements allow programmers to make decisions and repeat actions based on certain conditions.
    
    There are three main types of control statements in programming:
    1. Conditional statements (if, if-else, switch)
    2. Looping statements (for, while, do-while)
    3. Jump statements (break, continue, return)
    
    Conditional statements are used to execute different blocks of code based on whether a condition is true or false.
    The if statement is the most basic conditional statement. It executes a block of code only if the specified condition is true.
    The if-else statement provides an alternative block of code to execute when the condition is false.
    
    Looping statements are used to repeat a block of code multiple times. The for loop is commonly used when the number of iterations is known.
    The while loop continues executing as long as the specified condition remains true.
    
    Jump statements alter the normal flow of execution. The break statement terminates the current loop.
    The continue statement skips the rest of the current iteration and moves to the next iteration.
    """
    
    print("=== TESTING IMPROVED AI SUMMARY GENERATION ===\n")
    
    # Test AI summary
    print("1. Testing AI Summary Generation:")
    print("-" * 50)
    try:
        ai_summary = generate_summary_with_ai(sample_text)
        print(ai_summary)
        print(f"\nSummary Length: {len(ai_summary)} characters")
        print(f"Word Count: {len(ai_summary.split())} words")
        
        # Check for redundancy
        lines = ai_summary.split('\n')
        content_lines = [line.strip() for line in lines if line.strip() and not line.startswith('**')]
        unique_content = set(content_lines)
        redundancy_ratio = (len(content_lines) - len(unique_content)) / len(content_lines) if content_lines else 0
        print(f"Redundancy Check: {redundancy_ratio:.2%} redundant content")
        
    except Exception as e:
        print(f"AI Summary Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test fallback summary
    print("2. Testing Fallback Summary Generation:")
    print("-" * 50)
    try:
        fallback_summary = generate_smart_fallback_summary(sample_text)
        print(fallback_summary)
        print(f"\nSummary Length: {len(fallback_summary)} characters")
        print(f"Word Count: {len(fallback_summary.split())} words")
        
    except Exception as e:
        print(f"Fallback Summary Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test with short text
    print("3. Testing with Limited Content:")
    print("-" * 50)
    short_text = "This is a very short document with minimal content."
    short_summary = generate_smart_fallback_summary(short_text)
    print(short_summary)
    
    print("\n=== SUMMARY GENERATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_summary_improvements()