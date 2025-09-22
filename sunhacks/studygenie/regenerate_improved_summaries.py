#!/usr/bin/env python
"""
Regenerate summaries for existing documents with improved AI summary generation
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_summary_with_ai

def regenerate_all_summaries():
    """Regenerate summaries for all documents with improved algorithm"""
    
    documents = Document.objects.all()
    total_docs = documents.count()
    
    print(f"Found {total_docs} documents to process")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for i, doc in enumerate(documents, 1):
        print(f"Processing {i}/{total_docs}: {doc.title}")
        
        try:
            if doc.extracted_text and len(doc.extracted_text.strip()) > 50:
                # Generate new improved summary
                new_summary = generate_summary_with_ai(doc.extracted_text)
                
                if new_summary and len(new_summary.strip()) > 50:
                    doc.summary = new_summary
                    doc.save()
                    print(f"  [OK] Updated summary ({len(new_summary)} chars)")
                    success_count += 1
                else:
                    print(f"  [SKIP] Generated summary too short, keeping original")
                    error_count += 1
            else:
                print(f"  [SKIP] No extracted text available")
                error_count += 1
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            error_count += 1
    
    print("\n" + "=" * 50)
    print("Summary regeneration complete!")
    print(f"Successfully updated: {success_count} documents")
    print(f"Errors/Skipped: {error_count} documents")
    print(f"Total processed: {success_count + error_count} documents")

if __name__ == "__main__":
    regenerate_all_summaries()