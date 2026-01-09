from openai import AzureOpenAI
import os

def get_ai_client():
    try:
        return AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_KEY", "mock_key"),
            api_version="2024-02-01",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://mock.openai.azure.com")
        )
    except Exception:
        return None

client = get_ai_client()