import os
import urllib.request
import urllib.error
import json
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"
req = urllib.request.Request(
    url,
    headers={
        "Authorization": f"Bearer {key}", 
        "Content-Type": "application/json",
        "User-Agent": "ZomatoAI/1.0"
    },
    data=json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 10
    }).encode("utf-8")
)
try:
    with urllib.request.urlopen(req) as response:
        print("Response:", response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print("Other error:", e)
