#!/usr/bin/env python
"""
Test the new improved summary format
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_enhanced_fallback_summary, extract_key_terms_from_text, extract_main_topics

def test_new_format():
    """Test the new summary format"""
    
    # Get a document to test
    doc = Document.objects.filter(extracted_text__isnull=False).exclude(extracted_text='').first()
    
    if not doc:
        print("No documents found")
        return
    
    print(f"Testing document: {doc.title}")
    print("="*50)
    
    # Generate new formatted summary
    key_terms = extract_key_terms_from_text(doc.extracted_text)
    main_topics = extract_main_topics(doc.extracted_text)
    
    new_summary = generate_enhanced_fallback_summary(doc.extracted_text, key_terms, main_topics)
    
    print("NEW FORMATTED SUMMARY:")
    print("-"*30)
    print(new_summary)
    print("-"*30)
    print(f"Word count: {len(new_summary.split())} words")
    print(f"Character count: {len(new_summary)} characters")
    
    # Update the document
    update = input("\nUpdate this document's summary? (y/n): ").lower().strip()
    if update == 'y':
        doc.summary = new_summary
        doc.save()
        print("Summary updated!")

if __name__ == "__main__":
    test_new_format()