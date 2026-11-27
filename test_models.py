"""Test which Claude models are available with the API key."""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key present: {bool(api_key)}")

# Try different model names
models_to_try = [
    "claude-opus-4-1-20250805",
    "claude-3-5-sonnet-20241022",
    "claude-3-sonnet-20240229"
]

client = Anthropic(api_key=api_key)

for model in models_to_try:
    print(f"\nTrying {model}...")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'working'"}
            ]
        )
        print(f"[OK] {model} works!")
        print(f"Response: {response.content[0].text}")
        print(f"\n=== Use this model in .env: ===")
        print(f"LLM_MODEL={model}")
        break
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] {error_msg[:150]}")
