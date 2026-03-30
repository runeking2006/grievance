from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GrievanceCreate(BaseModel):
    complaint_text: str

class GrievanceRead(BaseModel):
    id: int
    complaint_text: str
    translated_text: Optional[str]
    category: Optional[str]
    urgency: Optional[str]
    department: Optional[str]
    language: Optional[str]
    timestamp: datetime
    is_repeated: bool

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_complaints: int
    categories: dict[str, int]
    high_priority: int
    repeated_issues: int
