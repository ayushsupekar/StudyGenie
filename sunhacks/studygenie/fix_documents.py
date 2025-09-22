#!/usr/bin/env python
"""
Fix documents that are missing AI-generated content
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from documents.views import extract_text_from_pdf, extract_text_from_image, generate_ai_summary

def fix_missing_summaries():
    print("=== Fixing Documents Missing AI Content ===")
    
    # Find documents without summaries
    missing_docs = Document.objects.filter(summary='').order_by('created_at')
    
    if not missing_docs.exists():
        print("✅ All documents already have summaries!")
        return
    
    print(f"Found {missing_docs.count()} documents missing summaries:")
    
    for doc in missing_docs:
        print(f"\n📄 Processing Document ID {doc.id}: {doc.title}")
        
        try:
            # Check if file exists
            if not os.path.exists(doc.file.path):
                print(f"   ❌ File not found: {doc.file.path}")
                doc.status = 'error'
                doc.save()
                continue
            
            # Extract text based on file type
            if doc.title.lower().endswith('.pdf'):
                print("   📖 Extracting text from PDF...")
                extracted_text = extract_text_from_pdf(doc.file.path)
            elif doc.title.lower().endswith(('.png', '.jpg', '.jpeg')):
                print("   🖼️ Extracting text from image...")
                extracted_text = extract_text_from_image(doc.file.path)
            else:
                print(f"   ❌ Unsupported file type: {doc.title}")
                continue
            
            print(f"   ✅ Extracted {len(extracted_text)} characters")
            
            # Generate AI summary
            print("   🤖 Generating AI summary...")
            summary = generate_ai_summary(extracted_text)
            print(f"   ✅ Generated summary: {len(summary)} characters")
            
            # Update document
            doc.extracted_text = extracted_text
            doc.summary = summary
            doc.status = 'processed'
            doc.save()
            
            print(f"   ✅ Document {doc.id} fixed successfully!")
            
        except Exception as e:
            print(f"   ❌ Error processing document {doc.id}: {e}")
            doc.status = 'error'
            doc.save()
            continue
    
    print(f"\n🎉 Processing complete!")
    
    # Show final status
    total_docs = Document.objects.count()
    processed_docs = Document.objects.filter(status='processed').count()
    error_docs = Document.objects.filter(status='error').count()
    uploaded_docs = Document.objects.filter(status='uploaded').count()
    
    print(f"\nFinal Status:")
    print(f"✅ Processed: {processed_docs}/{total_docs}")
    print(f"❌ Errors: {error_docs}/{total_docs}")
    print(f"⏳ Pending: {uploaded_docs}/{total_docs}")

if __name__ == "__main__":
    fix_missing_summaries()