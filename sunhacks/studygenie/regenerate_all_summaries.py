#!/usr/bin/env python
import os
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_summary_with_ai

def regenerate_all_summaries():
    print("=== Regenerating All Summaries with AI ===")
    
    # Get all documents
    docs = Document.objects.all()[:10]  # Process first 10 to avoid quota issues
    print(f"Processing {docs.count()} documents")
    
    updated_count = 0
    
    for i, doc in enumerate(docs):
        if doc.extracted_text and len(doc.extracted_text.strip()) > 100:
            print(f"\n{i+1}. Processing: {doc.title}")
            
            try:
                # Generate AI summary
                summary = generate_summary_with_ai(doc.extracted_text[:3000])  # Use first 3000 chars
                
                if summary and len(summary) > 50:
                    doc.summary = summary
                    doc.save()
                    updated_count += 1
                    print(f"✅ Updated with AI summary ({len(summary)} chars)")
                else:
                    print("❌ AI summary too short, keeping existing")
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"Skipping {doc.title} - insufficient content")
    
    print(f"\n=== Updated {updated_count} summaries ===")

if __name__ == "__main__":
    regenerate_all_summaries()