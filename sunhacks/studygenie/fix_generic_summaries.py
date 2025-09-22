#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_smart_fallback_summary

def fix_generic_summaries():
    print("=== Fixing Generic Summaries ===")
    
    # Get documents with generic summaries
    docs = Document.objects.filter(summary__contains="approximately")
    print(f"Found {docs.count()} documents with generic summaries")
    
    updated_count = 0
    
    for doc in docs:
        if doc.extracted_text and len(doc.extracted_text.strip()) > 50:
            print(f"Updating: {doc.title}")
            
            # Generate new summary using actual content
            new_summary = generate_smart_fallback_summary(doc.extracted_text)
            doc.summary = new_summary
            doc.save()
            updated_count += 1
            print("Summary updated successfully")
        else:
            print(f"Skipping {doc.title} - insufficient content")
    
    print(f"\n=== Updated {updated_count} summaries ===")

if __name__ == "__main__":
    fix_generic_summaries()