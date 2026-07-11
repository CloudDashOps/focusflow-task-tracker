from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os

from database import engine, get_db, Base, migrate_database
from models import Task

# Create tables
Base.metadata.create_all(bind=engine)
migrate_database()

app = FastAPI(title="Task Tracker API")

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    ).split(",")
    if origin.strip()
]

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Pydantic Schemas =============

class TaskCreate(BaseModel):
    title: str
    category: str = "General"
    priority: str = "medium"
    due_date: datetime | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    category: str | None = None
    priority: str | None = None
    due_date: datetime | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    category: str
    priority: str
    due_date: datetime | None
    created_at: datetime | None

    class Config:
        from_attributes = True

# ============= Endpoints =============

@app.get("/")
def read_root() -> dict:
    """Health check endpoint"""
    return {"message": "Task Tracker API is running"}

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)) -> List[TaskResponse]:
    """Fetch all tasks"""
    tasks = db.query(Task).all()
    return tasks

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """Create a new task"""
    if not task.title.strip():
        raise HTTPException(status_code=422, detail="Task title cannot be empty")
    new_task = Task(
        title=task.title.strip(),
        completed=False,
        category=task.category or "General",
        priority=task.priority or "medium",
        due_date=task.due_date
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Toggle completion status or update task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.title is not None:
        if not task_update.title.strip():
            raise HTTPException(status_code=422, detail="Task title cannot be empty")
        task.title = task_update.title.strip()
    if task_update.completed is not None:
        task.completed = task_update.completed
    if task_update.category is not None:
        task.category = task_update.category
    if task_update.priority is not None:
        task.priority = task_update.priority
    if "due_date" in task_update.model_fields_set:
        task.due_date = task_update.due_date
    
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
