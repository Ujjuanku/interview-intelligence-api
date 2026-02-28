import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
