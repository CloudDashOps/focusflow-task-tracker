from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password: str = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

class Task(Base):
    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), index=True)
    completed: bool = Column(Boolean, default=False)
    category: str = Column(String(50), default="General")
    priority: str = Column(String(20), default="medium")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
