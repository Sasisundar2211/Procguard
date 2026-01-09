from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.enforcement.engine import run_enforcement
from app.ai.violation_explainer import explain_violation
import os

router = APIRouter()

@router.post("/execute")
def execute_sop_verification(payload: dict):
    """
    Stateless endpoint for SOP execution verification.
    Proves deterministic enforcement.
    """
    sop = payload.get("procedure")
    execution = payload.get("execution")
    roles = payload.get("roles")

    if not sop or not execution or not roles:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # 1. Deterministic Enforcement (AUTHORITATIVE)
    violation = run_enforcement(
        sop_steps=sop["steps"],
        execution_events=execution,
        role_map=roles
    )

    if violation:
        # 2. AI Explanation (NON-AUTHORITATIVE)
        explanation = None
        if os.getenv("AI_ENABLED", "true").lower() == "true":
            try:
                # Mock AI call if key is missing or use placeholder
                # Note: explain_violation calls Azure OpenAI
                if "AZURE_OPENAI_KEY" in os.environ:
                    explanation = explain_violation(violation["code"])
                else:
                    explanation = f"AI Explanation for {violation['code']}: [AI Service Mocked]"
            except Exception:
                explanation = "AI Explanation Service Unavailable"

        return JSONResponse(
            status_code=403,
            content={
                "status": "VIOLATED",
                "violation": violation,
                "explanation": explanation
            }
        )

    return {
        "status": "SUCCESS",
        "violation": None
    }
