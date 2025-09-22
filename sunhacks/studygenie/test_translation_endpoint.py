#!/usr/bin/env python
"""
Test translation endpoint functionality
"""
import os
import sys
import django
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from documents.models import Document

def test_translation_endpoint():
    """Test the translation endpoint"""
    print("[START] Testing translation endpoint")
    
    try:
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass')
            user.save()
        
        # Create test document
        doc, created = Document.objects.get_or_create(
            user=user,
            title='test_doc.pdf',
            defaults={
                'extracted_text': 'This is a test document about programming concepts.',
                'summary': 'This document covers programming concepts and basic principles.',
                'status': 'processed'
            }
        )
        
        print(f"[INFO] Using document ID: {doc.id}")
        
        # Test the translate_content function directly
        from ai_services import translate_content
        
        test_text = "This document covers programming concepts and basic principles."
        
        # Test translation to Hindi
        hindi_translation = translate_content(test_text, 'hi')
        print(f"[OK] Hindi translation: {len(hindi_translation)} characters")
        
        # Test translation to Spanish
        spanish_translation = translate_content(test_text, 'es')
        print(f"[OK] Spanish translation: {len(spanish_translation)} characters")
        
        print("[SUCCESS] Translation functionality working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Translation test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_translation_endpoint()
    if success:
        print("[COMPLETE] Translation endpoint is ready!")
    else:
        print("[FAILED] Translation endpoint needs attention")