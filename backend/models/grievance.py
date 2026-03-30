from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Grievance(SQLModel, table=True):
    __tablename__ = "grievance"

    id: int | None = Field(default=None, primary_key=True)
    complaint_text: str
    translated_text: str | None = None
    category: str | None = Field(default=None, index=True)
    urgency: str | None = None
    embedding: str | None = None
    embedding_key: str | None = Field(default=None, index=True)
    department: str | None = Field(default=None, index=True)
    language: str | None = None
    location: str | None = Field(default=None, index=True)
    user_id: str | None = Field(default=None, index=True)
    user_email: str | None = None
    is_repeated: bool = Field(default=False)
    escalated: bool = Field(default=False, index=True)
    escalation_level: int = Field(default=0)
    status: str = Field(default="Pending")
    processing_status: str = Field(default="completed", index=True)
    latest_insight: str | None = None
    deadline: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("timestamp", DateTime(timezone=True), nullable=False, index=True),
    )
