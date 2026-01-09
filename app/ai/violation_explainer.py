from app.ai.client import client

def explain_violation(code: str) -> str:
    """
    Human-readable explanation only.
    No side effects.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Explain this violation in plain English."},
            {"role": "user", "content": code}
        ]
    )

    return response.choices[0].message.content