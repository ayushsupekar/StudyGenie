#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from quizzes.models import Quiz, Question
from flashcards.models import Flashcard
from ai_services import generate_quiz_with_ai, generate_flashcards_with_ai

def test_backend():
    print("=== Testing StudyGenie Backend ===")
    
    # Test 1: Check if documents exist
    print("\n1. Checking documents...")
    docs = Document.objects.all()
    print(f"Found {docs.count()} documents")
    
    if docs.exists():
        doc = docs.first()
        print(f"Testing with document: {doc.title}")
        
        # Test 2: AI Services
        print("\n2. Testing AI services...")
        try:
            quiz_data = generate_quiz_with_ai("This is a test document about machine learning concepts.")
            print(f"Quiz generation: SUCCESS - {len(quiz_data)} questions")
        except Exception as e:
            print(f"Quiz generation: FAILED - {e}")
        
        try:
            flashcard_data = generate_flashcards_with_ai("This is a test document about machine learning concepts.")
            print(f"Flashcard generation: SUCCESS - {len(flashcard_data)} cards")
        except Exception as e:
            print(f"Flashcard generation: FAILED - {e}")
        
        # Test 3: Database operations
        print("\n3. Testing database operations...")
        
        # Check quizzes
        quizzes = Quiz.objects.filter(document=doc)
        print(f"Quizzes for {doc.title}: {quizzes.count()}")
        
        # Check flashcards
        flashcards = Flashcard.objects.filter(document=doc)
        print(f"Flashcards for {doc.title}: {flashcards.count()}")
        
    else:
        print("No documents found. Upload a document first.")
    
    print("\n=== Backend Test Complete ===")

if __name__ == "__main__":
    test_backend()