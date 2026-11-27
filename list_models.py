"""List available models with the API key."""
import os
os.environ.pop('ANTHROPIC_BASE_URL', None)
os.environ.pop('ANTHROPIC_AUTH_TOKEN', None)

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"Testing with API Key: {api_key[:30]}...")

import anthropic

# Try to list available models
try:
    client = anthropic.Anthropic(api_key=api_key)

    # Try the models.list() endpoint if available
    models = client.models.list()
    print(f"\nAvailable models:")
    for model in models.data:
        print(f"  - {model.id}")

except AttributeError:
    print("Models listing not available in this SDK version")

except Exception as e:
    print(f"Could not list models: {e}")
    print("\nTrying direct API call...")

    import requests
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json"
    }

    try:
        response = requests.get(
            "https://api.anthropic.com/v1/models",
            headers=headers,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e2:
        print(f"Direct API call failed: {e2}")
