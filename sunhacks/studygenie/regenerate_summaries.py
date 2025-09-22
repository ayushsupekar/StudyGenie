
#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_smart_fallback_summary, generate_summary_with_ai

def regenerate_summaries():
    print("=== Regenerating ALL Summaries ===")
    
    # Get all documents
    docs = Document.objects.all()
    print(f"Found {docs.count()} documents")
    
    updated_count = 0
    
    for doc in docs:
        if doc.extracted_text and len(doc.extracted_text.strip()) > 50:
            print(f"\nProcessing: {doc.title}")
            
            try:
                # Try AI summary first
                new_summary = generate_summary_with_ai(doc.extracted_text, 'medium')
                if not new_summary or len(new_summary.strip()) < 20:
                    # Fallback to smart summary
                    new_summary = generate_smart_fallback_summary(doc.extracted_text)
                
                # Always update summary
                doc.summary = new_summary
                doc.save()
                updated_count += 1
                print(f"Updated: {new_summary[:80]}...")
                
            except Exception as e:
                print(f"Error processing {doc.title}: {e}")
                # Use fallback
                new_summary = generate_smart_fallback_summary(doc.extracted_text)
                doc.summary = new_summary
                doc.save()
                updated_count += 1
        else:
            print(f"Skipping {doc.title} - insufficient text")
    
    print(f"\n=== Updated {updated_count} summaries ===")

if __name__ == "__main__":
    regenerate_summaries()