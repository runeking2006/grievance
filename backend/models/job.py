from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class ComplaintJob(SQLModel, table=True):
    __tablename__ = "complaint_job"

    id: int | None = Field(default=None, primary_key=True)
    grievance_id: int = Field(index=True)
    job_type: str = Field(default="enrich_complaint", index=True)
    status: str = Field(default="queued", index=True)
    worker_backend: str = Field(default="local", index=True)
    task_ref: str | None = Field(default=None, index=True)
    run_after: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
    )
    attempts: int = Field(default=0)
    error_message: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
