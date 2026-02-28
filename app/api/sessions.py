from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.session import SessionCreate, SessionResponse, SessionDetailResponse, RoundCreate, RoundResponse
from app.services.session_service import (
    create_session, 
    get_user_sessions, 
    get_session_detail, 
    add_evaluation_round,
    complete_session
)
from app.services.auth_service import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def init_session(
    session_in: SessionCreate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Creates a new interview session."""
    return await create_session(db, current_user.id, session_in)

@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Lists all past and active interview sessions for the user."""
    return await get_user_sessions(db, current_user.id)

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full details of a specific interview session, including its rounds."""
    return await get_session_detail(db, current_user.id, session_id)

@router.post("/{session_id}/add-round", response_model=RoundResponse, status_code=status.HTTP_201_CREATED)
async def add_round(
    session_id: str, 
    round_in: RoundCreate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Saves an evaluation result tightly coupled into the interview session."""
    return await add_evaluation_round(db, current_user.id, session_id, round_in)

@router.post("/{session_id}/complete", response_model=SessionResponse)
async def finish_session(
    session_id: str, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Marks an interview session as completed."""
    return await complete_session(db, current_user.id, session_id)
