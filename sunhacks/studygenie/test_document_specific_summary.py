#!/usr/bin/env python
"""
Test document-specific summary generation
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from ai_services import generate_summary_with_ai
from documents.models import Document

def test_document_specific_summary():
    """Test that summaries are specific to document content"""
    
    # Test with actual document
    doc = Document.objects.first()
    if doc and doc.extracted_text:
        print(f"Testing with document: {doc.title}")
        print("=" * 50)
        
        # Show original text preview
        text_preview = doc.extracted_text[:300] + "..." if len(doc.extracted_text) > 300 else doc.extracted_text
        print("Document Content Preview:")
        print(text_preview)
        print("\n" + "-" * 50)
        
        # Generate summary
        summary = generate_summary_with_ai(doc.extracted_text)
        print("Generated Summary:")
        print(summary)
        print(f"\nSummary Length: {len(summary)} characters")
        
        # Check if summary contains document-specific terms
        doc_words = set(doc.extracted_text.lower().split())
        summary_words = set(summary.lower().split())
        common_words = doc_words & summary_words
        
        print(f"Common terms between document and summary: {len(common_words)}")
        
        # Check for generic terms that shouldn't be in document-specific summary
        generic_terms = ['educational material', 'study material', 'learning concepts', 'foundational knowledge']
        has_generic = any(term in summary.lower() for term in generic_terms)
        
        if has_generic:
            print("WARNING: Summary contains generic terms")
        else:
            print("GOOD: Summary appears document-specific")
            
    else:
        print("No documents with extracted text found")

if __name__ == "__main__":
    test_document_specific_summary()