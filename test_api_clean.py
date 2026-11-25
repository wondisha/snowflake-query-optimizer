"""Test API key with environment properly cleared."""
# Clear environment FIRST before any imports
import os
os.environ.pop('ANTHROPIC_BASE_URL', None)
os.environ.pop('ANTHROPIC_AUTH_TOKEN', None)

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"Testing API Key: {api_key[:30]}...")

# Check environment is clean
print(f"ANTHROPIC_BASE_URL set: {'ANTHROPIC_BASE_URL' in os.environ}")
print(f"ANTHROPIC_AUTH_TOKEN set: {'ANTHROPIC_AUTH_TOKEN' in os.environ}\n")

import anthropic
client = anthropic.Anthropic(api_key=api_key)

print("Sending test message to claude-3-5-sonnet-20241022...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=50,
    messages=[{"role": "user", "content": "Say hello"}]
)

print(f"[SUCCESS] ✓ API key works!")
print(f"Response: {response.content[0].text}")
