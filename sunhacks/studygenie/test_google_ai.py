#!/usr/bin/env python
import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

# Test Google AI connection
def test_google_ai_connection():
    try:
        import google.generativeai as genai
        
        # Check if API key is loaded
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        print(f"API Key loaded: {'Yes' if api_key and api_key != 'your-google-ai-key' else 'No'}")
        print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")
        
        if not api_key or api_key == 'your-google-ai-key':
            print("ERROR: Google AI API key not configured")
            return False
            
        # Configure and test API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Testing Google AI API connection...")
        response = model.generate_content("Say 'Hello from StudyGenie with Google AI!'")
        
        result = response.text.strip()
        print(f"SUCCESS: Google AI API working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"ERROR: Google AI API Error: {e}")
        return False

if __name__ == "__main__":
    print("=== StudyGenie Google AI API Test ===")
    test_google_ai_connection()