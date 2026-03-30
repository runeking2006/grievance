from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class UserAccount(SQLModel, table=True):
    __tablename__ = "user_account"

    id: str = Field(primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    api_key_hash: str = Field(index=True, unique=True)
    role: str = Field(default="student", index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
