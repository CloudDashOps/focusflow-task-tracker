from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
import os

from auth import authenticate_user, create_access_token, get_current_user, get_password_hash, get_user_by_email
from database import engine, get_db, Base, migrate_database
from models import Task, User

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

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

# ============= Endpoints =============

@app.get("/")
def read_root() -> dict:
    """Health check endpoint"""
    return {"message": "Task Tracker API is running"}

@app.post("/auth/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    """Create a new user account"""
    if len(user.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="A user with that email already exists")
    new_user = User(
        email=user.email.lower().strip(),
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.email})
    return TokenResponse(access_token=access_token)

@app.post("/auth/login", response_model=TokenResponse)
def login(user: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return a JWT token"""
    authenticated_user = authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": authenticated_user.email})
    return TokenResponse(access_token=access_token)

@app.get("/auth/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get the currently authenticated user"""
    return current_user

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[TaskResponse]:
    """Fetch tasks for the authenticated user"""
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TaskResponse:
    """Create a new task"""
    if not task.title.strip():
        raise HTTPException(status_code=422, detail="Task title cannot be empty")
    new_task = Task(
        title=task.title.strip(),
        completed=False,
        category=task.category or "General",
        priority=task.priority or "medium",
        due_date=task.due_date,
        user_id=current_user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """Toggle completion status or update task"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
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
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
