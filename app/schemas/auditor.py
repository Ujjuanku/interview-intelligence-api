from pydantic import BaseModel, Field
from typing import List, Literal

class AuditRequest(BaseModel):
    question: str = Field(..., description="The interview question being answered")
    candidate_answer: str = Field(..., description="The candidate's response")
    resume_context: str = Field(..., description="The relevant resume chunk context used for this question")
    evaluation_json: dict = Field(..., description="The JSON output from the AI evaluation agent")

class AuditResponse(BaseModel):
    grounded: bool = Field(..., description="Whether the evaluation is logically grounded")
    hallucination_detected: bool = Field(..., description="True if fabricated criticism or ungrounded claims are detected")
    unsupported_claims: List[str] = Field(..., description="List of unsupported or fabricated claims in the evaluation")
    reasoning_alignment_score: int = Field(..., ge=1, le=10, description="Score from 1 to 10 for reasoning alignment")
    score_consistency: Literal["Consistent", "Inconsistent"] = Field(..., description="Consistency of the score with the reasoning")
    verdict: Literal["Valid Evaluation", "Potential Hallucination"] = Field(..., description="Final verdict on the evaluation")
