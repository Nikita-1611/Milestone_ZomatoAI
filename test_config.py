from backend.config import load_backend_settings
import os

print("CWD:", os.getcwd())
settings = load_backend_settings()
print("KEY:", settings.groq_api_key)
