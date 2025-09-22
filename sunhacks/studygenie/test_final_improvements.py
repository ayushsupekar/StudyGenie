#!/usr/bin/env python
"""
Test the final improvements to summary generation and YouTube search
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from documents.models import Document
from ai_services import generate_enhanced_fallback_summary, extract_key_terms_from_text, extract_main_topics
from youtube_services import get_video_recommendations_from_summary

def test_improvements():
    """Test the final improvements"""
    
    # Get a document to test
    doc = Document.objects.filter(extracted_text__isnull=False).exclude(extracted_text='').first()
    
    if not doc:
        print("No documents found")
        return
    
    print(f"Testing improvements for: {doc.title}")
    print("="*60)
    
    # Test improved summary generation
    print("\\n1. TESTING IMPROVED SUMMARY GENERATION")
    print("-"*40)
    
    key_terms = extract_key_terms_from_text(doc.extracted_text)
    main_topics = extract_main_topics(doc.extracted_text)
    
    new_summary = generate_enhanced_fallback_summary(doc.extracted_text, key_terms, main_topics)
    
    print(f"Key Terms Found: {', '.join(key_terms[:5])}")
    print(f"Main Topics: {', '.join(main_topics[:3])}")
    print(f"\\nNEW SUMMARY ({len(new_summary.split())} words):")
    print(new_summary)
    
    # Test improved YouTube search
    print("\\n\\n2. TESTING IMPROVED YOUTUBE SEARCH")
    print("-"*40)
    
    videos, keywords = get_video_recommendations_from_summary(new_summary, doc.title)
    
    print(f"Search Keywords Used: {', '.join(keywords)}")
    print(f"Videos Found: {len(videos)}")
    
    for i, video in enumerate(videos, 1):
        print(f"\\n{i}. {video['title']}")
        print(f"   Channel: {video['channel']}")
        print(f"   URL: {video['url']}")
    
    # Ask if user wants to update
    print("\\n" + "="*60)
    update = input("Update this document with new summary? (y/n): ").lower().strip()
    if update == 'y':
        doc.summary = new_summary
        doc.save()
        print("Document updated successfully!")
    else:
        print("Document not updated")

if __name__ == "__main__":
    test_improvements()