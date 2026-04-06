import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.gemini_provider import GeminiProvider

load_dotenv()
print(f"API_KEY: {os.getenv('API_KEY')}")
print(f"BASE_URL: {os.getenv('BASE_URL')}")

llm = GeminiProvider()
try:
    res = llm.generate("Chào bạn, bạn là ai?")
    print("Response successful!")
    print(res["content"])
except Exception as e:
    print(f"Error type: {type(e)}")
    print(f"Error: {e}")
