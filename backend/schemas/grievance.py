from pydantic import BaseModel
from datetime import datetime


class ComplaintCreate(BaseModel):
    text: str
    location: str | None = None


class ComplaintResponse(BaseModel):
    complaint_id: int | None = None
    category: str
    urgency: str
    department: str
    insight: str
    status: str
    deadline: datetime | None
    similar_complaints: list[str]
    processing_status: str
    owner_id: str | None = None
    escalated: bool = False
    escalation_level: int = 0


class DashboardStats(BaseModel):
    total: int
    categories: dict[str, int]
    high_priority: int
    repeated: int
    bottleneck: str | None
    bottleneck_count: int


class RepeatedComplaint(BaseModel):
    complaint_text: str
    count: int


class BottleneckResponse(BaseModel):
    bottleneck: str
    reason: str
    complaints: int


class HighPriorityComplaint(BaseModel):
    complaint_text: str
    department: str | None
    status: str
    deadline: datetime | None
    created_at: datetime


class AreaInsight(BaseModel):
    location: str
    issue: str
    count: int
    insight: str


class UserRegister(BaseModel):
    email: str
    full_name: str | None = None


class TokenRequest(BaseModel):
    email: str
    api_key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    role: str
    api_key: str | None = None


class ComplaintJobResponse(BaseModel):
    job_id: int
    grievance_id: int
    status: str
    job_type: str
    error_message: str | None = None


class OwnedComplaint(BaseModel):
    complaint_id: int
    complaint_text: str
    category: str | None
    urgency: str | None
    department: str | None
    status: str
    processing_status: str
    escalated: bool
    escalation_level: int
    created_at: datetime
