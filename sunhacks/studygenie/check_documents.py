#!/usr/bin/env python
"""
Check existing documents in database
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from django.contrib.auth.models import User

def check_existing_documents():
    print("=== Checking Existing Documents ===")
    
    try:
        # Get all documents
        documents = Document.objects.all().order_by('-created_at')
        print(f"Total documents in database: {documents.count()}")
        
        if documents.count() == 0:
            print("No documents found in database.")
            return
        
        print("\nDocument Details:")
        print("-" * 80)
        
        for i, doc in enumerate(documents[:10], 1):  # Show first 10
            print(f"{i}. ID: {doc.id}")
            print(f"   Title: {doc.title}")
            print(f"   User: {doc.user.username}")
            print(f"   Status: {doc.status}")
            print(f"   Created: {doc.created_at}")
            print(f"   Has extracted text: {bool(doc.extracted_text)} ({len(doc.extracted_text)} chars)")
            print(f"   Has summary: {bool(doc.summary)} ({len(doc.summary)} chars)")
            
            if doc.summary:
                print(f"   Summary preview: {doc.summary[:100]}...")
            else:
                print("   Summary: MISSING - This is the issue!")
            
            print("-" * 40)
        
        # Check for documents without summaries
        no_summary = documents.filter(summary='')
        if no_summary.exists():
            print(f"\n⚠️  Found {no_summary.count()} documents WITHOUT summaries!")
            print("These documents need to be reprocessed.")
            
            # Offer to fix them
            print("\nWould you like to regenerate summaries for these documents?")
            print("Run: python fix_documents.py")
        else:
            print("\n✅ All documents have summaries!")
            
    except Exception as e:
        print(f"Error checking documents: {e}")
        import traceback
        traceback.print_exc()

def check_users():
    print("\n=== Checking Users ===")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        doc_count = Document.objects.filter(user=user).count()
        print(f"- {user.username}: {doc_count} documents")

if __name__ == "__main__":
    check_existing_documents()
    check_users()