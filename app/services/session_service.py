from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
import uuid

from app.models.session import InterviewSession, RoundEvaluation
from app.schemas.session import SessionCreate, RoundCreate

async def create_session(db: AsyncSession, user_id: str, session_in: SessionCreate) -> InterviewSession:
    db_session = InterviewSession(
        user_id=user_id,
        role=session_in.role
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

async def get_user_sessions(db: AsyncSession, user_id: str) -> list[InterviewSession]:
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
    )
    return result.scalars().all()

async def get_session_detail(db: AsyncSession, user_id: str, session_id: str) -> InterviewSession:
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.rounds))
        .where(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not owned by user.")
    return session

async def add_evaluation_round(db: AsyncSession, user_id: str, session_id: str, round_in: RoundCreate) -> RoundEvaluation:
    # Verify session ownership first
    session = await get_session_detail(db, user_id, session_id)
    
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Cannot add round to a completed session.")
        
    next_round_num = len(session.rounds) + 1
    
    eval_data = round_in.round_evaluation
    
    db_round = RoundEvaluation(
        session_id=session_id,
        round_number=next_round_num,
        final_score=eval_data.final_score,
        hallucination_detected=eval_data.audit.hallucination_detected,
        reasoning_alignment_score=eval_data.audit.reasoning_alignment_score,
        score_consistency=eval_data.audit.score_consistency,
        raw_evaluation_json=eval_data.model_dump()
    )
    
    db.add(db_round)
    await db.commit()
    await db.refresh(db_round)
    return db_round

async def complete_session(db: AsyncSession, user_id: str, session_id: str) -> InterviewSession:
    session = await get_session_detail(db, user_id, session_id)
    session.status = "completed"
    await db.commit()
    await db.refresh(session)
    return session
