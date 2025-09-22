#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document

def debug_summary():
    print("=== Debugging Summary Display ===")
    
    # Get all documents
    docs = Document.objects.all()
    print(f"Found {docs.count()} documents")
    
    for doc in docs:
        print(f"\n--- Document: {doc.title} ---")
        print(f"ID: {doc.id}")
        print(f"Status: {doc.status}")
        print(f"Summary exists: {bool(doc.summary)}")
        if doc.summary:
            print(f"Summary length: {len(doc.summary)} characters")
            print(f"Summary preview: {doc.summary[:100]}...")
        else:
            print("No summary found")
        
        print(f"Extracted text exists: {bool(doc.extracted_text)}")
        if doc.extracted_text:
            print(f"Text length: {len(doc.extracted_text)} characters")
            print(f"Text preview: {doc.extracted_text[:100]}...")
        else:
            print("No extracted text found")

if __name__ == "__main__":
    debug_summary()