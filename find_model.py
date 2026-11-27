"""Find which Claude model is available."""
import os
os.environ.pop('ANTHROPIC_BASE_URL', None)
os.environ.pop('ANTHROPIC_AUTH_TOKEN', None)

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"Testing API Key: {api_key[:30]}...\n")

import anthropic
client = anthropic.Anthropic(api_key=api_key)

# Try different models
models = [
    "claude-opus-4-1-20250805",
    "claude-opus-4-1",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet",
    "claude-3-sonnet-20240229",
    "claude-3-sonnet",
    "claude-3-haiku-20240307"
]

for model in models:
    try:
        print(f"Trying {model}...", end=" ")
        response = client.messages.create(
            model=model,
            max_tokens=20,
            messages=[{"role": "user", "content": "hi"}]
        )
        print(f"✓ WORKS!")
        print(f"Response: {response.content[0].text}")
        print(f"\n=== SUCCESS ===")
        print(f"Use this model in .env:")
        print(f"LLM_MODEL={model}")
        break
    except anthropic.NotFoundError:
        print("❌ Not found")
    except Exception as e:
        print(f"❌ Error: {str(e)[:60]}")
