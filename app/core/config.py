import os

DATABASE_URL = os.getenv("DATABASE_URL")
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Set it as an environment variable."
    )
