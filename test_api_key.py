"""Test Anthropic API key directly."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"Testing API Key: {api_key[:30]}...")
print(f"Key length: {len(api_key)}")
print(f"Key format valid: {api_key.startswith('sk-ant-usr-')}\n")

try:
    # Import after environment variables are set
    import anthropic

    # Create client
    client = anthropic.Anthropic(api_key=api_key)
    print(f"Anthropic SDK version: {anthropic.__version__}")
    print(f"Client created successfully\n")

    # Try a simple message
    print("Sending test message to Claude...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )

    print(f"[SUCCESS] API key works!")
    print(f"Response: {response.content[0].text}")

except anthropic.APIError as e:
    print(f"[API Error] Status: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"Error type: {type(e).__name__}")
    print(f"\nFull error: {e}")

    # Try to get more details
    if hasattr(e, 'response'):
        print(f"\nResponse headers: {e.response.headers if hasattr(e.response, 'headers') else 'N/A'}")

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
