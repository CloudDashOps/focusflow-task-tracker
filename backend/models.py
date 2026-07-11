from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), index=True)
    completed: bool = Column(Boolean, default=False)
    category: str = Column(String(50), default="General")
    priority: str = Column(String(20), default="medium")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
