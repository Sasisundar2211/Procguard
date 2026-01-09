from app.ai.client import client

def parse_sop_to_steps(sop_text: str) -> dict:
    """
    NON-AUTHORITATIVE.
    AI suggests structure. Code validates.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract SOP steps into a structured JSON format."
            },
            {
                "role": "user",
                "content": sop_text
            }
        ]
    )

    return response.choices[0].message.content