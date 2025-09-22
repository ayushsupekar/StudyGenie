#!/usr/bin/env python
import os
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_summary_with_ai

def simple_regenerate():
    print("=== Regenerating Summaries ===")
    
    # Get documents that need better summaries
    docs = Document.objects.all()[:5]  # Process first 5
    print(f"Processing {docs.count()} documents")
    
    updated_count = 0
    
    for i, doc in enumerate(docs):
        if doc.extracted_text and len(doc.extracted_text.strip()) > 100:
            print(f"{i+1}. Processing: {doc.title}")
            
            try:
                # Generate AI summary
                summary = generate_summary_with_ai(doc.extracted_text[:3000])
                
                if summary and len(summary) > 50:
                    doc.summary = summary
                    doc.save()
                    updated_count += 1
                    print(f"Updated successfully ({len(summary)} chars)")
                
                time.sleep(2)  # Delay to avoid rate limiting
                
            except Exception as e:
                print(f"Error: {str(e)}")
    
    print(f"Updated {updated_count} summaries")

if __name__ == "__main__":
    simple_regenerate()