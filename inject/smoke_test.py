#!/usr/bin/env python3
"""Direct smoke test against MiniMax API.

Run INSIDE the container with:
  docker exec -it <container> python3 /tmp/smoke_test.py <your_api_key>

Tests 3 things:
1. Direct curl to /v1/models with the api key
2. anthropic SDK with the api key
3. langchain_anthropic ChatAnthropic with the api key
"""
import sys
import os
import json

api_key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MINIMAX_API_KEY")
if not api_key:
    print("Usage: python3 smoke_test.py <api_key>")
    print("  or set MINIMAX_API_KEY env var")
    sys.exit(1)

print(f"API key length: {len(api_key)}")
print(f"API key starts with: {api_key[:8]}...")
print(f"API key ends with: ...{api_key[-4:]}")
print()

BASE = "https://api.minimax.io/anthropic"

# Test 1: Direct HTTP call
print("=" * 60)
print("TEST 1: Direct HTTP call to /v1/models")
print("=" * 60)
try:
    import requests
    r = requests.get(
        f"{BASE}/v1/models",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        timeout=30,
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if "data" in data:
            models = [m.get("id", m.get("name", "?")) for m in data["data"]]
            print(f"Models ({len(models)}): {models[:5]}...")
        else:
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Error: {r.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

# Test 2: anthropic SDK
print()
print("=" * 60)
print("TEST 2: anthropic SDK")
print("=" * 60)
try:
    from anthropic import Anthropic
    client = Anthropic(
        api_key=api_key,
        base_url=BASE,
    )
    msg = client.messages.create(
        model="MiniMax-M3",
        max_tokens=50,
        messages=[{"role": "user", "content": "hi"}],
    )
    print(f"Status: OK")
    for block in msg.content:
        if block.type == "text":
            print(f"Response: {block.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Test 3: langchain_anthropic
print()
print("=" * 60)
print("TEST 3: langchain_anthropic.ChatAnthropic")
print("=" * 60)
try:
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(
        model="MiniMax-M3",
        anthropic_api_key=api_key,
        anthropic_api_url=BASE,
        max_tokens=50,
    )
    from langchain_core.messages import HumanMessage
    result = llm.invoke([HumanMessage(content="hi")])
    print(f"Status: OK")
    print(f"Response: {result.content[:200]}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
