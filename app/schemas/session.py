from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
from app.schemas.decision import RoundEvaluation as DecisionRoundEvaluation

class SessionCreate(BaseModel):
    role: str = Field(..., description="Role being interviewed for")

class SessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class RoundCreate(BaseModel):
    round_evaluation: DecisionRoundEvaluation

class RoundResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    round_number: int
    final_score: int
    hallucination_detected: bool
    reasoning_alignment_score: int
    score_consistency: str
    raw_evaluation_json: dict
    created_at: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    rounds: List[RoundResponse] = []
