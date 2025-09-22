#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_summary_with_ai

def test_new_api():
    print("=== Testing New API Key ===")
    
    # Get a document to test
    doc = Document.objects.first()
    if doc and doc.extracted_text:
        print(f"Testing with: {doc.title}")
        print(f"Text length: {len(doc.extracted_text)} characters")
        
        # Test AI summary generation
        try:
            summary = generate_summary_with_ai(doc.extracted_text[:2000])  # Use first 2000 chars
            print(f"AI Summary generated successfully!")
            print(f"Summary: {summary}")
            
            # Update the document
            doc.summary = summary
            doc.save()
            print("Document updated with new AI summary")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No suitable document found for testing")

if __name__ == "__main__":
    test_new_api()