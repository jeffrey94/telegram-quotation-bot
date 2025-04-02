import os
import sys
from openai import OpenAI

def test_openai_key():
    # Get the API key
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set")
        return False
    
    print(f"API key found (starts with '{api_key[:4]}...')")
    
    try:
        # Try to initialize the client
        client = OpenAI(api_key=api_key)
        
        # Make a simple API call
        response = client.models.list()
        
        # If we got here, it worked!
        print(f"SUCCESS: OpenAI API connection works!")
        print(f"Available models: {len(response.data)} models found")
        return True
    
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_key()
    sys.exit(0 if success else 1) 