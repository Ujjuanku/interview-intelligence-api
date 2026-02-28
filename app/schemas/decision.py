from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class RoundAudit(BaseModel):
    hallucination_detected: bool = Field(..., description="Whether a hallucination was detected in this round's evaluation")
    reasoning_alignment_score: int = Field(..., description="Alignment score from 1-10")
    score_consistency: str = Field(..., description="Consistent or Inconsistent")

class RoundEvaluation(BaseModel):
    scores: dict = Field(..., description="Dictionary containing the 4 score axes")
    weaknesses: List[str] = Field(default=[], description="List of weaknesses identified in the round")
    final_score: int = Field(..., description="The final score out of 100 for this round")
    audit: RoundAudit = Field(..., description="The audit results for this evaluation")

class DecisionRequest(BaseModel):
    role: str = Field(..., description="The role the candidate is interviewing for")
    rounds: List[RoundEvaluation] = Field(..., description="The evaluated rounds for this candidate")

class DecisionResponse(BaseModel):
    overall_average: float = Field(..., description="The overall average rating out of 10")
    consistency_trend: str = Field(..., description="E.g., Stable, Variable, Improving")
    recurring_weaknesses: List[str] = Field(..., description="Weaknesses seen across multiple rounds")
    dominant_strengths: List[str] = Field(..., description="Strengths consistently shown")
    hallucination_risk_flag: bool = Field(..., description="True if any round had a hallucination detected")
    overall_confidence: Literal["Low", "Medium", "High"] = Field(..., description="Confidence in this decision")
    hire_recommendation: Literal["Strong Hire", "Hire", "Leaning Hire", "Leaning No Hire", "No Hire"] = Field(..., description="The final hiring recommendation")
    justification: str = Field(..., description="A brief text justification aggregating the structured data")
