#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import detect_language, generate_summary_with_ai, generate_quiz_with_ai, generate_flashcards_with_ai

def test_indian_languages():
    print("=== Testing Indian Languages Support ===")
    
    # Test texts in English, Hindi, and Marathi
    test_texts = {
        'english': "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
        'hindi': "मशीन लर्निंग कृत्रिम बुद्धिमत्ता का एक हिस्सा है जो डेटा से सीखने वाले एल्गोरिदम पर केंद्रित है। यह तकनीक कंप्यूटर को बिना स्पष्ट प्रोग्रामिंग के सीखने की क्षमता देती है।",
        'marathi': "मशीन लर्निंग हे कृत्रिम बुद्धिमत्तेचा एक भाग आहे जो डेटावरून शिकणाऱ्या अल्गोरिदमवर केंद्रित आहे। हे तंत्रज्ञान संगणकाला स्पष्ट प्रोग्रामिंग न करता शिकण्याची क्षमता देते।"
    }
    
    for lang, text in test_texts.items():
        print(f"\n--- Testing {lang.upper()} ---")
        
        # Test language detection
        detected = detect_language(text)
        print(f"Expected: {lang}, Detected: {detected}")
        
        # Test summary generation
        try:
            summary = generate_summary_with_ai(text)
            print(f"Summary: {summary[:100]}...")
        except Exception as e:
            print(f"Summary error: {e}")
        
        # Test quiz generation
        try:
            quiz = generate_quiz_with_ai(text)
            print(f"Quiz questions: {len(quiz)}")
        except Exception as e:
            print(f"Quiz error: {e}")
        
        # Test flashcard generation
        try:
            flashcards = generate_flashcards_with_ai(text)
            print(f"Flashcards: {len(flashcards)}")
            if flashcards:
                print(f"Sample flashcard: {flashcards[0]['front'][:50]}...")
        except Exception as e:
            print(f"Flashcard error: {e}")
    
    print("\n=== Indian Languages Test Complete ===")

if __name__ == "__main__":
    test_indian_languages()