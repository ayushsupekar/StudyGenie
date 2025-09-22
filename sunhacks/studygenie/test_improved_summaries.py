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
    
    print("🔍 Testing Improved Summary Generation")
    print("=" * 50)
    
    # Get some documents to test
    documents = Document.objects.filter(extracted_text__isnull=False).exclude(extracted_text='')[:5]
    
    if not documents:
        print("❌ No documents found with extracted text")
        return
    
    for doc in documents:
        print(f"\n📄 Document: {doc.title}")
        print(f"📅 Created: {doc.created_at}")
        print(f"📊 Text Length: {len(doc.extracted_text)} characters")
        
        # Extract analysis data
        key_terms = extract_key_terms_from_text(doc.extracted_text)
        main_topics = extract_main_topics(doc.extracted_text)
        doc_type = detect_document_type(doc.extracted_text)
        
        print(f"🏷️  Document Type: {doc_type}")
        print(f"🔑 Key Terms: {', '.join(key_terms[:8])}")
        print(f"📋 Main Topics: {', '.join(main_topics[:3])}")
        
        # Show old summary
        print(f"\n📝 OLD SUMMARY ({len(doc.summary)} chars):")
        print(f"   {doc.summary[:200]}{'...' if len(doc.summary) > 200 else ''}")
        
        # Generate new improved summary
        try:
            new_summary = generate_summary_with_ai(doc.extracted_text)
            
            print(f"\n✨ NEW IMPROVED SUMMARY ({len(new_summary)} chars):")
            print(f"   {new_summary[:300]}{'...' if len(new_summary) > 300 else ''}")
            
            # Check if new summary is more specific
            is_old_specific = is_summary_specific(doc.summary, key_terms)
            is_new_specific = is_summary_specific(new_summary, key_terms)
            
            print(f"\n📊 QUALITY ANALYSIS:")
            print(f"   Old Summary Specific: {'✅' if is_old_specific else '❌'}")
            print(f"   New Summary Specific: {'✅' if is_new_specific else '❌'}")
            
            # Count key terms in summaries
            old_terms_count = sum(1 for term in key_terms if term.lower() in doc.summary.lower())
            new_terms_count = sum(1 for term in key_terms if term.lower() in new_summary.lower())
            
            print(f"   Key Terms in Old: {old_terms_count}/{len(key_terms)}")
            print(f"   Key Terms in New: {new_terms_count}/{len(key_terms)}")
            
            improvement = "🚀 IMPROVED" if (is_new_specific and new_terms_count > old_terms_count) else "📊 SIMILAR"
            print(f"   Overall: {improvement}")
            
        except Exception as e:
            print(f"❌ Error generating new summary: {e}")
        
        print("-" * 50)

def regenerate_all_summaries():
    """Regenerate summaries for all documents with the improved algorithm"""
    
    print("\n🔄 Regenerating All Document Summaries")
    print("=" * 50)
    
    documents = Document.objects.filter(extracted_text__isnull=False).exclude(extracted_text='')
    total_docs = documents.count()
    
    if total_docs == 0:
        print("❌ No documents found with extracted text")
        return
    
    print(f"📊 Found {total_docs} documents to process")
    
    updated_count = 0
    error_count = 0
    
    for i, doc in enumerate(documents, 1):
        print(f"\n📄 Processing {i}/{total_docs}: {doc.title[:50]}...")
        
        try:
            # Generate improved summary
            old_summary = doc.summary
            new_summary = generate_summary_with_ai(doc.extracted_text)
            
            # Only update if new summary is significantly different and better
            if (new_summary and len(new_summary) > 80 and 
                new_summary != old_summary and
                len(new_summary) > len(old_summary) * 0.8):  # At least 80% of old length
                
                # Check quality improvement
                key_terms = extract_key_terms_from_text(doc.extracted_text)
                old_terms_count = sum(1 for term in key_terms if term.lower() in old_summary.lower())
                new_terms_count = sum(1 for term in key_terms if term.lower() in new_summary.lower())
                
                if new_terms_count >= old_terms_count:  # New summary has same or more key terms
                    doc.summary = new_summary
                    doc.save()
                    updated_count += 1
                    print(f"   ✅ Updated (Key terms: {old_terms_count} → {new_terms_count})")
                else:
                    print(f"   ⚠️  Skipped (Quality not improved)")
            else:
                print(f"   ⚠️  Skipped (No significant improvement)")
                
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 REGENERATION COMPLETE")
    print(f"   ✅ Updated: {updated_count}")
    print(f"   ⚠️  Skipped: {total_docs - updated_count - error_count}")
    print(f"   ❌ Errors: {error_count}")

def test_specific_document(doc_id):
    """Test improved summary on a specific document"""
    
    try:
        doc = Document.objects.get(id=doc_id)
        print(f"🔍 Testing Document ID: {doc_id}")
        print(f"📄 Title: {doc.title}")
        print(f"📊 Text Length: {len(doc.extracted_text)} characters")
        
        # Show current summary
        print(f"\n📝 CURRENT SUMMARY:")
        print(f"   {doc.summary}")
        
        # Generate new summary
        new_summary = generate_summary_with_ai(doc.extracted_text)
        print(f"\n✨ NEW IMPROVED SUMMARY:")
        print(f"   {new_summary}")
        
        # Analysis
        key_terms = extract_key_terms_from_text(doc.extracted_text)
        print(f"\n🔑 Key Terms Found: {', '.join(key_terms[:10])}")
        
        old_terms = sum(1 for term in key_terms if term.lower() in doc.summary.lower())
        new_terms = sum(1 for term in key_terms if term.lower() in new_summary.lower())
        
        print(f"📊 Key Terms in Current: {old_terms}/{len(key_terms)}")
        print(f"📊 Key Terms in New: {new_terms}/{len(key_terms)}")
        
        # Ask if user wants to update
        update = input(f"\n🤔 Update document summary? (y/n): ").lower().strip()
        if update == 'y':
            doc.summary = new_summary
            doc.save()
            print("✅ Document summary updated!")
        else:
            print("⚠️  Document not updated")
            
    except Document.DoesNotExist:
        print(f"❌ Document with ID {doc_id} not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 StudyGenie - Improved Summary Testing")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_summary_improvements()
        elif sys.argv[1] == "regenerate":
            regenerate_all_summaries()
        elif sys.argv[1] == "doc" and len(sys.argv) > 2:
            doc_id = int(sys.argv[2])
            test_specific_document(doc_id)
        else:
            print("Usage:")
            print("  python test_improved_summaries.py test          # Test improvements")
            print("  python test_improved_summaries.py regenerate   # Regenerate all")
            print("  python test_improved_summaries.py doc <id>     # Test specific document")
    else:
        print("Available commands:")
        print("1. Test improvements on sample documents")
        print("2. Regenerate all document summaries")
        print("3. Test specific document")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            test_summary_improvements()
        elif choice == "2":
            regenerate_all_summaries()
        elif choice == "3":
            doc_id = input("Enter document ID: ").strip()
            try:
                test_specific_document(int(doc_id))
            except ValueError:
                print("❌ Invalid document ID")
        else:
            print("❌ Invalid choice")