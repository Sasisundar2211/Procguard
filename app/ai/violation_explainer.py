from app.ai.client import get_ai_client

def explain_violation(code: str) -> str:
    """
    Human-readable explanation only.
    No side effects.
    """

    client = get_ai_client()
    if not client:
        return f"Explanation for {code} is currently unavailable (AI disabled)."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Explain this violation in plain English."},
            {"role": "user", "content": code}
        ]
    )

    return response.choices[0].message.content