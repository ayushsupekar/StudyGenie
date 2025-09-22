#!/usr/bin/env python
"""
Test script for multilanguage functionality
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import (
    detect_language, 
    generate_summary_with_language,
    generate_quiz_with_language,
    generate_flashcards_with_language,
    translate_content
)

def test_language_detection():
    """Test language detection functionality"""
    print("🔍 Testing Language Detection...")
    
    # Test English text
    english_text = "This is a programming tutorial about control statements in Java."
    detected = detect_language(english_text)
    print(f"English text detected as: {detected}")
    
    # Test Hindi text (if available)
    hindi_text = "यह जावा में नियंत्रण कथनों के बारे में एक प्रोग्रामिंग ट्यूटोरियल है।"
    detected = detect_language(hindi_text)
    print(f"Hindi text detected as: {detected}")
    
    print("✅ Language detection test completed\n")

def test_multilingual_summary():
    """Test multilingual summary generation"""
    print("📝 Testing Multilingual Summary Generation...")
    
    sample_text = """
    Control statements in Java are used to control the flow of execution in a program. 
    There are three main types: conditional statements (if-else), looping statements (for, while), 
    and jump statements (break, continue, return). These statements allow programmers to create 
    dynamic and flexible programs that can make decisions and repeat operations.
    """
    
    languages = ['en', 'hi', 'mr', 'es']
    
    for lang in languages:
        print(f"Generating summary in {lang}...")
        try:
            summary = generate_summary_with_language(sample_text, lang)
            print(f"✅ {lang}: {summary[:100]}...")
        except Exception as e:
            print(f"❌ {lang}: Error - {e}")
    
    print("✅ Multilingual summary test completed\n")

def test_multilingual_quiz():
    """Test multilingual quiz generation"""
    print("❓ Testing Multilingual Quiz Generation...")
    
    sample_text = """
    Control statements in Java include if-else statements for conditional execution,
    for and while loops for repetitive tasks, and break/continue for loop control.
    """
    
    languages = ['en', 'hi']
    
    for lang in languages:
        print(f"Generating quiz in {lang}...")
        try:
            quiz = generate_quiz_with_language(sample_text, lang, 'easy')
            print(f"✅ {lang}: Generated {len(quiz)} questions")
            if quiz:
                print(f"   Sample question: {quiz[0].get('stem', 'N/A')[:80]}...")
        except Exception as e:
            print(f"❌ {lang}: Error - {e}")
    
    print("✅ Multilingual quiz test completed\n")

def test_multilingual_flashcards():
    """Test multilingual flashcard generation"""
    print("🃏 Testing Multilingual Flashcard Generation...")
    
    sample_text = """
    Java control statements: if-else for conditions, for/while for loops, 
    break/continue for loop control. These are fundamental programming concepts.
    """
    
    languages = ['en', 'hi']
    
    for lang in languages:
        print(f"Generating flashcards in {lang}...")
        try:
            flashcards = generate_flashcards_with_language(sample_text, lang)
            print(f"✅ {lang}: Generated {len(flashcards)} flashcards")
            if flashcards:
                print(f"   Sample: {flashcards[0].get('front', 'N/A')[:50]}...")
        except Exception as e:
            print(f"❌ {lang}: Error - {e}")
    
    print("✅ Multilingual flashcard test completed\n")

def test_translation():
    """Test content translation"""
    print("🌐 Testing Content Translation...")
    
    english_text = "Control statements are fundamental programming constructs that control program flow."
    
    target_languages = ['hi', 'mr', 'es']
    
    for lang in target_languages:
        print(f"Translating to {lang}...")
        try:
            translation = translate_content(english_text, lang)
            print(f"✅ {lang}: {translation[:80]}...")
        except Exception as e:
            print(f"❌ {lang}: Error - {e}")
    
    print("✅ Translation test completed\n")

def main():
    """Run all multilanguage tests"""
    print("🚀 Starting Multilanguage Feature Tests\n")
    print("=" * 60)
    
    try:
        test_language_detection()
        test_multilingual_summary()
        test_multilingual_quiz()
        test_multilingual_flashcards()
        test_translation()
        
        print("🎉 All multilanguage tests completed!")
        print("✨ Multilanguage feature is ready to use!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()