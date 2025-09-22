#!/usr/bin/env python
"""
Debug script to test upload process step by step
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from django.contrib.auth.models import User
from documents.models import Document
from documents.views import extract_text_from_pdf, generate_ai_summary
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_pdf():
    """Create a simple test PDF content"""
    # This is a minimal PDF content for testing
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World! This is a test PDF.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""
    return pdf_content

def test_full_upload_process():
    print("=== Testing Full Upload Process ===")
    
    try:
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass')
            user.save()
        
        print(f"Using user: {user.username}")
        
        # Create test file
        test_content = """
        Machine Learning Fundamentals
        
        Machine learning is a subset of artificial intelligence that enables computers to learn 
        and make decisions from data without being explicitly programmed for every task.
        
        Key Types:
        1. Supervised Learning - Uses labeled training data
        2. Unsupervised Learning - Finds patterns in unlabeled data  
        3. Reinforcement Learning - Learns through trial and error
        
        Common algorithms include linear regression, decision trees, neural networks, and clustering.
        Applications span from recommendation systems to autonomous vehicles.
        """
        
        # Create uploaded file object
        uploaded_file = SimpleUploadedFile(
            "test_ml_document.txt",
            test_content.encode('utf-8'),
            content_type="text/plain"
        )
        
        print(f"Created test file: {uploaded_file.name}")
        print(f"File size: {uploaded_file.size} bytes")
        
        # Create document
        doc = Document.objects.create(
            user=user,
            title=uploaded_file.name,
            file=uploaded_file
        )
        
        print(f"Document created with ID: {doc.id}")
        print(f"File path: {doc.file.path}")
        
        # Test text extraction (simulate)
        extracted_text = test_content  # Since it's already text
        print(f"Extracted text length: {len(extracted_text)} characters")
        
        # Test AI summary generation
        print("Generating AI summary...")
        summary = generate_ai_summary(extracted_text)
        print(f"Summary length: {len(summary)} characters")
        print(f"Summary preview: {summary[:200]}...")
        
        # Update document
        doc.extracted_text = extracted_text
        doc.summary = summary
        doc.status = 'processed'
        doc.save()
        
        print(f"Document updated successfully!")
        print(f"Status: {doc.status}")
        
        # Test AI content generation
        from ai_services import generate_quiz_with_ai, generate_flashcards_with_ai
        
        print("Generating quiz questions...")
        quiz = generate_quiz_with_ai(extracted_text)
        print(f"Generated {len(quiz)} quiz questions")
        
        print("Generating flashcards...")
        flashcards = generate_flashcards_with_ai(extracted_text)
        print(f"Generated {len(flashcards)} flashcards")
        
        # Verify document can be retrieved
        retrieved_doc = Document.objects.get(id=doc.id)
        print(f"Retrieved document: {retrieved_doc.title}")
        print(f"Has summary: {bool(retrieved_doc.summary)}")
        print(f"Has extracted text: {bool(retrieved_doc.extracted_text)}")
        
        print("SUCCESS: Full upload process completed!")
        
        # Clean up
        doc.delete()
        print("Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_upload_process()
    if success:
        print("\n🎉 Upload process is working correctly!")
        print("If you're still having issues, check:")
        print("1. Make sure you're logged in")
        print("2. Check browser console for JavaScript errors")
        print("3. Verify file permissions in media directory")
        print("4. Check Django server logs for detailed error messages")
    else:
        print("\n❌ Upload process has issues. Check the errors above.")