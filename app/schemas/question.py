from pydantic import BaseModel, Field
from typing import List

class QuestionRequest(BaseModel):
    role: str = Field(..., description="The role the candidate is interviewing for (e.g., Backend Engineer)")

class QuestionResponse(BaseModel):
    questions: List[str] = Field(..., description="List of generated interview questions")
