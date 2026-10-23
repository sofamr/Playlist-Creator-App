import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

ENV_PATH = Path(__file__).resolve().parent / ".env"

def load_or_request_api_key() -> str:
    """Load Gemini API key from .env or prompt the user to input and save it."""
    load_dotenv(dotenv_path=ENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # Check if empty or still placeholder
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n" + "=" * 60)
        print("Google Gemini API Key Setup")
        print("=" * 60)
        print("You can get a free API key at: https://aistudio.google.com/app/apikey")
        print("You can also paste it directly into the `.env` file.")
        print("=" * 60)
        api_key = input("Enter your Gemini API key: ").strip()

        if not api_key:
            raise ValueError("No Gemini API key provided. Cannot proceed with AI sorting.")

        # Save to .env for future runs
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"# Google Gemini API Key\nGEMINI_API_KEY={api_key}\n")
        print(f"API key saved to {ENV_PATH.name} for future runs!\n")

    return api_key


def get_gemini_client() -> genai.Client:
    """Initialize and return a Gemini API client."""
    api_key = load_or_request_api_key()
    return genai.Client(api_key=api_key)
