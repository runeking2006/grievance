from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Grievance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    complaint_text: str
    translated_text: Optional[str] = None
    category: Optional[str] = None
    urgency: Optional[str] = None
    department: Optional[str] = None
    language: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_repeated: bool = Field(default=False)
