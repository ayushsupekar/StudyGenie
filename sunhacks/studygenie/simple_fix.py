#!/usr/bin/env python
"""
Simple fix for documents missing AI content
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from documents.views import extract_text_from_pdf, generate_ai_summary

def fix_documents():
    print("Fixing documents missing AI content...")
    
    # Find documents without summaries
    missing_docs = Document.objects.filter(summary='')
    print(f"Found {missing_docs.count()} documents to fix")
    
    for doc in missing_docs:
        print(f"Processing: {doc.title} (ID: {doc.id})")
        
        try:
            # Extract text from PDF
            if doc.title.lower().endswith('.pdf'):
                extracted_text = extract_text_from_pdf(doc.file.path)
                print(f"Extracted {len(extracted_text)} characters")
                
                # Generate summary
                summary = generate_ai_summary(extracted_text)
                print(f"Generated summary: {len(summary)} characters")
                
                # Update document
                doc.extracted_text = extracted_text
                doc.summary = summary
                doc.status = 'processed'
                doc.save()
                
                print(f"Fixed document {doc.id}")
            else:
                print(f"Skipping non-PDF: {doc.title}")
                
        except Exception as e:
            print(f"Error fixing {doc.id}: {e}")
            doc.status = 'error'
            doc.save()
    
    print("Fix complete!")

if __name__ == "__main__":
    fix_documents()