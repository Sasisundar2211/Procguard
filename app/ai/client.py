from openai import AzureOpenAI
import os

_client = None

def get_ai_client():
    global _client
    if _client is not None:
        return _client
        
    api_key = os.environ.get("AZURE_OPENAI_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    
    if not api_key or not endpoint:
        return None
        
    try:
        _client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-01",
            azure_endpoint=endpoint
        )
        return _client
    except Exception:
        return None