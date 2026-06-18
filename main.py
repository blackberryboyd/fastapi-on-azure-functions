from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from fastapi.routing import APIRouter

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pathlib import Path

from models import ExerciseLog

import json
import os
from database import engine, Base, get_db

# Shot exercise keywords used to compute "total shots" (we match variants via LIKE)
SHOT_KEYWORDS = ["slap", "wrist", "snap", "backhand"]
SHOT_PATTERNS = [f"%{k}%" for k in SHOT_KEYWORDS]


BASE_DIR = "."
DB_PATH = os.path.join(BASE_DIR, "app.db")

app = FastAPI()
root_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(root_dir)), name="static")
router = APIRouter()
# Add this line to your main.py
app.include_router(router)

@app.on_event("startup")
def startup_event():
    print("--- STARTUP: Initializing database ---")
    try:
        print(f"Creating tables with engine: {engine}")
        print(f"Base metadata tables: {Base.metadata.tables.keys()}")
        Base.metadata.create_all(bind=engine)
        print(f"--- SUCCESS: Database created at {DB_PATH} ---")
        print(f"Database URL: {engine.url}")
    except Exception as e:
        print(f"--- FAILURE: Database could not be created: {e} ---")

@app.get("/")
async def read_index():
    return FileResponse(root_dir / "index.html")

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from your Azure backend!"}


# Allow your frontend (on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/button-click")
async def handle_button():
    return {"message": "Success! The Python backend received your click."}



# Pydantic model for data validation from the browser
class LogCreate(BaseModel):
    name: str
    exercise: str
    amount: float


@router.post("/api/log-exercise")
async def log_exercise(data: LogCreate, db: Session = Depends(get_db)):
    # Create the object, letting the database handle 'id' and 'date'
    
    new_entry = ExerciseLog(
            name=data.name,
            exercise=data.exercise,
            amount=data.amount
    )
    try:
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return {"status": "success"}
    except SQLAlchemyError as e:
        db.rollback()  # Always rollback on error!
        # Print the error to your terminal to see the details
        print(f"DATABASE ERROR: {e}") 
        raise HTTPException(status_code=400, detail="Could not save to database")

    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

@app.get("/api/get-names")
async def get_names(db: Session = Depends(get_db)):
    # 1. Get defaults from a file
    with open("names.json", "r") as f:
        defaults = json.load(f)
    
    # 2. Get unique names from database
    db_names = [n[0] for n in db.query(ExerciseLog.name).distinct().all()]
    
    # 3. Combine and return unique set
    return list(set(defaults + db_names))


@app.get("/api/leaderboard/{exercise}")
async def leaderboard(exercise: str, limit: int = 10, db: Session = Depends(get_db)):
    # Normalize exercise name for case-insensitive matching
    norm = (exercise or "").strip().lower()

    # Special-case "total shots" to aggregate multiple shot exercises
    if norm == "total shots":
        cond = None
        for p in SHOT_PATTERNS:
            expr = func.lower(ExerciseLog.exercise).like(p)
            cond = expr if cond is None else (cond | expr)
        rows = (
            db.query(ExerciseLog.name, func.sum(ExerciseLog.amount).label("total"))
            .filter(cond)
            .group_by(ExerciseLog.name)
            .order_by(func.sum(ExerciseLog.amount).desc())
            .limit(limit)
            .all()
        )
    else:
        rows = (
            db.query(ExerciseLog.name, func.sum(ExerciseLog.amount).label("total"))
            .filter(func.lower(ExerciseLog.exercise) == norm)
            .group_by(ExerciseLog.name)
            .order_by(func.sum(ExerciseLog.amount).desc())
            .limit(limit)
            .all()
        )
    return [{"name": r[0], "total": r[1]} for r in rows]


@app.get("/api/leaderboards")
async def all_leaderboards(limit: int = 10, db: Session = Depends(get_db)):
    # Aggregate totals per exercise and name
    rows = (
        db.query(ExerciseLog.exercise, ExerciseLog.name, func.sum(ExerciseLog.amount).label("total"))
        .group_by(ExerciseLog.exercise, ExerciseLog.name)
        .all()
    )
    result = {}
    for exercise, name, total in rows:
        result.setdefault(exercise, []).append({"name": name, "total": total})

    # Add a combined "total shots" leaderboard (aggregate across shot types)
    cond = None
    for p in SHOT_PATTERNS:
        expr = func.lower(ExerciseLog.exercise).like(p)
        cond = expr if cond is None else (cond | expr)
    shot_rows = (
        db.query(ExerciseLog.name, func.sum(ExerciseLog.amount).label("total"))
        .filter(cond)
        .group_by(ExerciseLog.name)
        .all()
    )
    if shot_rows:
        result.setdefault("total shots", []).extend([{"name": r[0], "total": r[1]} for r in shot_rows])

    # Sort each exercise leaderboard and apply limit
    for ex in list(result.keys()):
        result[ex] = sorted(result[ex], key=lambda x: x["total"], reverse=True)[:limit]

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)