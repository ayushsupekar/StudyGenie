#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import detect_language, generate_summary_with_ai, generate_quiz_with_ai, generate_flashcards_with_ai

def test_multilingual():
    print("=== Testing Multilingual AI Features ===")
    
    # Test texts in different languages
    test_texts = {
        'english': "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
        'spanish': "El aprendizaje automático es un subconjunto de la inteligencia artificial que se centra en algoritmos que pueden aprender de los datos.",
        'french': "L'apprentissage automatique est un sous-ensemble de l'intelligence artificielle qui se concentre sur les algorithmes qui peuvent apprendre à partir de données.",
        'german': "Maschinelles Lernen ist eine Teilmenge der künstlichen Intelligenz, die sich auf Algorithmen konzentriert, die aus Daten lernen können.",
        'italian': "L'apprendimento automatico è un sottoinsieme dell'intelligenza artificiale che si concentra su algoritmi che possono imparare dai dati.",
        'portuguese': "O aprendizado de máquina é um subconjunto da inteligência artificial que se concentra em algoritmos que podem aprender com dados."
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
    
    print("\n=== Multilingual Test Complete ===")

if __name__ == "__main__":
    test_multilingual()