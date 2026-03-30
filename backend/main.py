from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlmodel import Session, select
from typing import List

from database import init_db, get_session
from models import Grievance
from schemas import GrievanceCreate, GrievanceRead, DashboardStats
from services import process_grievance

app = FastAPI(title="Grievance AI System API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/grievances/", response_model=GrievanceRead)
def create_grievance(grievance: GrievanceCreate, db: Session = Depends(get_session)):
    processed = process_grievance(grievance.complaint_text)
    
    # Check for repeated issues (simple exact match or similar logic)
    # For MVP, we'll check if the same category has been reported many times recently
    # or if the exact text exists.
    existing = db.exec(select(Grievance).where(Grievance.complaint_text == grievance.complaint_text)).first()
    if existing:
        processed.is_repeated = True

    db.add(processed)
    db.commit()
    db.refresh(processed)
    return processed

@app.get("/grievances/", response_model=List[GrievanceRead])
def read_grievances(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    grievances = db.exec(select(Grievance).offset(skip).limit(limit)).all()
    return grievances

@app.get("/stats/", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_session)):
    total = db.exec(select(func.count(Grievance.id))).one()
    
    # Categories counts
    categories_query = db.exec(select(Grievance.category, func.count(Grievance.id)).group_by(Grievance.category)).all()
    categories_map = {cat: count for cat, count in categories_query if cat}
    
    high_priority = db.exec(select(func.count(Grievance.id)).where(Grievance.urgency == "High")).one()
    repeated = db.exec(select(func.count(Grievance.id)).where(Grievance.is_repeated == True)).one()
    
    return DashboardStats(
        total_complaints=total,
        categories=categories_map,
        high_priority=high_priority,
        repeated_issues=repeated
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
