from pydantic import BaseModel, Field
from typing import List

class EvaluationRequest(BaseModel):
    question: str = Field(..., description="The interview question being answered")
    answer: str = Field(..., description="The candidate's response")
    resume_context: str = Field(..., description="The relevant resume chunk context used for this question")

class Scores(BaseModel):
    conceptual_clarity: int = Field(..., ge=0, le=10, description="Clarity and correctness of technical concepts")
    technical_depth: int = Field(..., ge=0, le=10, description="Depth of technical knowledge demonstrated")
    real_world_application: int = Field(..., ge=0, le=10, description="Ability to apply knowledge to real-world scenarios or trade-offs")
    communication_precision: int = Field(..., ge=0, le=10, description="Clarity, structure, and precision of the answer")

class EvaluationResponse(BaseModel):
    scores: Scores
    confidence_level: str = Field(..., description="Low | Medium | High")
    strengths: List[str] = Field(..., description="Key strengths in the candidate's answer")
    weaknesses: List[str] = Field(..., description="Areas where the answer lacked depth or correctness")
    improvement_suggestions: List[str] = Field(..., description="Actionable suggestions for improvement")
    final_score: int = Field(..., ge=0, le=100, description="Aggregate score out of 100")
