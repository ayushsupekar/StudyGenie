#!/usr/bin/env python
"""
Test and regenerate improved summaries for existing documents
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import (
    generate_summary_with_ai, 
    extract_key_terms_from_text, 
    extract_main_topics, 
    generate_enhanced_fallback_summary,
    detect_document_type,
    is_summary_specific
)

def test_summary_improvements():
    """Test the improved summary generation on existing documents"""
    
    print("Testing Improved Summary Generation")
    print("="*50)
    
    # Get some documents to test
    documents = Document.objects.filter(extracted_text__isnull=False).exclude(extracted_text='')[:3]
    
    if not documents:
        print("No documents found with extracted text")
        return
    
    for doc in documents:
        print(f"\nDocument: {doc.title}")
        print(f"Created: {doc.created_at}")
        print(f"Text Length: {len(doc.extracted_text)} characters")
        
        # Extract analysis data
        key_terms = extract_key_terms_from_text(doc.extracted_text)
        main_topics = extract_main_topics(doc.extracted_text)
        doc_type = detect_document_type(doc.extracted_text)
        
        print(f"Document Type: {doc_type}")
        print(f"Key Terms: {', '.join(key_terms[:8])}")
        print(f"Main Topics: {', '.join(main_topics[:3])}")
        
        # Show old summary
        print(f"\nOLD SUMMARY ({len(doc.summary)} chars):")
        print(f"   {doc.summary[:200]}{'...' if len(doc.summary) > 200 else ''}")
        
        # Generate new improved summary
        try:
            new_summary = generate_summary_with_ai(doc.extracted_text)
            
            print(f"\nNEW IMPROVED SUMMARY ({len(new_summary)} chars):")
            print(f"   {new_summary[:300]}{'...' if len(new_summary) > 300 else ''}")
            
            # Check if new summary is more specific
            is_old_specific = is_summary_specific(doc.summary, key_terms)
            is_new_specific = is_summary_specific(new_summary, key_terms)
            
            print(f"\nQUALITY ANALYSIS:")
            print(f"   Old Summary Specific: {'YES' if is_old_specific else 'NO'}")
            print(f"   New Summary Specific: {'YES' if is_new_specific else 'NO'}")
            
            # Count key terms in summaries
            old_terms_count = sum(1 for term in key_terms if term.lower() in doc.summary.lower())
            new_terms_count = sum(1 for term in key_terms if term.lower() in new_summary.lower())
            
            print(f"   Key Terms in Old: {old_terms_count}/{len(key_terms)}")
            print(f"   Key Terms in New: {new_terms_count}/{len(key_terms)}")
            
            improvement = "IMPROVED" if (is_new_specific and new_terms_count > old_terms_count) else "SIMILAR"
            print(f"   Overall: {improvement}")
            
        except Exception as e:
            print(f"Error generating new summary: {e}")
        
        print("-" * 50)

def regenerate_specific_document(doc_id):
    """Regenerate summary for a specific document"""
    try:
        doc = Document.objects.get(id=doc_id)
        print(f"Processing Document: {doc.title}")
        
        # Generate new summary
        new_summary = generate_summary_with_ai(doc.extracted_text)
        
        print(f"\nOLD SUMMARY:")
        print(doc.summary)
        
        print(f"\nNEW SUMMARY:")
        print(new_summary)
        
        # Update the document
        doc.summary = new_summary
        doc.save()
        
        print(f"\nDocument summary updated successfully!")
        
    except Document.DoesNotExist:
        print(f"Document with ID {doc_id} not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("StudyGenie - Improved Summary Testing")
    print("="*50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_summary_improvements()
        elif sys.argv[1] == "update" and len(sys.argv) > 2:
            doc_id = int(sys.argv[2])
            regenerate_specific_document(doc_id)
        else:
            print("Usage:")
            print("  python test_improved_summaries_simple.py test")
            print("  python test_improved_summaries_simple.py update <doc_id>")
    else:
        test_summary_improvements()