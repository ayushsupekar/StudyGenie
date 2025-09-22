#!/usr/bin/env python
import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

# Test OpenAI connection
def test_openai_connection():
    try:
        from ai_services import client
        
        # Check if API key is loaded
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"API Key loaded: {'Yes' if api_key and api_key != 'sk-your-openai-api-key-here' else 'No'}")
        print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")
        
        if not client:
            print("❌ OpenAI client not initialized")
            return False
            
        # Test API call
        print("Testing OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello from StudyGenie!'"}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content.strip()
        print(f"SUCCESS: OpenAI API working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"ERROR: OpenAI API Error: {e}")
        return False

if __name__ == "__main__":
    print("=== StudyGenie OpenAI API Test ===")
    test_openai_connection()