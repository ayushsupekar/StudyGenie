#!/usr/bin/env python
"""
Test script to simulate document upload and processing
"""
import os
import sys
import django
from io import BytesIO

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from django.contrib.auth.models import User
from documents.models import Document
from documents.views import extract_text_from_pdf, generate_ai_summary
from ai_services import generate_summary_with_ai

def test_document_processing():
    print("Testing Document Processing...")
    
    # Test text extraction and AI generation
    test_text = """
    Introduction to Machine Learning
    
    Machine learning is a method of data analysis that automates analytical model building. 
    It is a branch of artificial intelligence (AI) based on the idea that systems can learn 
    from data, identify patterns and make decisions with minimal human intervention.
    
    Key Concepts:
    1. Supervised Learning - Learning with labeled examples
    2. Unsupervised Learning - Finding patterns in data without labels
    3. Reinforcement Learning - Learning through interaction and feedback
    
    Applications include image recognition, natural language processing, and recommendation systems.
    """
    
    print(f"\n1. Testing with sample text ({len(test_text)} characters)")
    
    try:
        # Test AI summary generation
        print("Generating AI summary...")
        summary = generate_ai_summary(test_text)
        print(f"Summary generated: {len(summary)} characters")
        print(f"Summary preview: {summary[:200]}...")
        
        # Test AI services directly
        print("\nTesting AI services directly...")
        from ai_services import generate_quiz_with_ai, generate_flashcards_with_ai
        
        quiz = generate_quiz_with_ai(test_text)
        print(f"Quiz questions generated: {len(quiz)}")
        
        flashcards = generate_flashcards_with_ai(test_text)
        print(f"Flashcards generated: {len(flashcards)}")
        
        print("\n✓ All processing steps completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    print("\nTesting Database Operations...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass')
            user.save()
            print("Created test user")
        else:
            print("Using existing test user")
        
        # Create a test document
        doc = Document.objects.create(
            user=user,
            title='test_document.txt',
            extracted_text='This is test content for the document.',
            summary='This is a test summary.',
            status='processed'
        )
        
        print(f"Created test document with ID: {doc.id}")
        
        # Verify document was saved
        saved_doc = Document.objects.get(id=doc.id)
        print(f"Retrieved document: {saved_doc.title}")
        print(f"Status: {saved_doc.status}")
        print(f"Summary length: {len(saved_doc.summary)}")
        
        # Clean up
        doc.delete()
        print("Test document cleaned up")
        
        print("✓ Database operations working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== StudyGenie Upload Test ===")
    
    success1 = test_document_processing()
    success2 = test_database_operations()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Upload functionality should work.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")