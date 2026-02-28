import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String, nullable=False)
    status = Column(String, default="active", nullable=False) # active, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="sessions")
    rounds = relationship("RoundEvaluation", back_populates="session", cascade="all, delete-orphan")

class RoundEvaluation(Base):
    __tablename__ = "round_evaluations"

    id = Column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )
    session_id = Column(String, ForeignKey("interview_sessions.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    
    # Store aggregated scores or flat items requested
    final_score = Column(Integer, nullable=False)
    hallucination_detected = Column(Boolean, nullable=False)
    reasoning_alignment_score = Column(Integer, nullable=False)
    score_consistency = Column(String, nullable=False)
    
    # Store dynamic structure since we can fallback locally on sqlite
    raw_evaluation_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="rounds")
