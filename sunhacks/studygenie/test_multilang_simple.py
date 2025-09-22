#!/usr/bin/env python
"""
Simple test script for multilanguage functionality
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import detect_language, generate_summary_with_language

def test_basic_functionality():
    """Test basic multilanguage functionality"""
    print("[START] Testing basic multilanguage functionality")
    
    # Test language detection
    print("[TEST] Language detection...")
    english_text = "This is a programming tutorial about control statements in Java."
    detected = detect_language(english_text)
    print(f"[RESULT] English text detected as: {detected}")
    
    # Test multilingual summary
    print("[TEST] Multilingual summary generation...")
    sample_text = """
    Control statements in Java are used to control the flow of execution in a program. 
    There are three main types: conditional statements (if-else), looping statements (for, while), 
    and jump statements (break, continue, return).
    """
    
    try:
        # Test English summary
        summary_en = generate_summary_with_language(sample_text, 'en')
        print(f"[OK] English summary: {len(summary_en)} characters")
        
        # Test Hindi summary
        summary_hi = generate_summary_with_language(sample_text, 'hi')
        print(f"[OK] Hindi summary: {len(summary_hi)} characters")
        
        print("[SUCCESS] Basic multilanguage functionality working!")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("[COMPLETE] Multilanguage feature is ready!")
    else:
        print("[FAILED] Multilanguage feature needs attention")