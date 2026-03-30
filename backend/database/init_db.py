from sqlalchemy import inspect, text
from sqlmodel import SQLModel

from backend.config.settings import settings
from backend.database.connection import engine
from backend.models.grievance import Grievance
from backend.models.job import ComplaintJob
from backend.models.user import UserAccount
from backend.services.vector_store import ensure_vector_schema


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    ensure_vector_schema(engine)
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("grievance")}
    user_columns = {column["name"] for column in inspector.get_columns("user_account")}
    job_columns = {column["name"] for column in inspector.get_columns("complaint_job")}
    with engine.begin() as connection:
        if "embedding" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN embedding TEXT"))
        if "embedding_key" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN embedding_key VARCHAR"))
        if "status" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN status VARCHAR DEFAULT 'Pending'"))
        if "processing_status" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN processing_status VARCHAR DEFAULT 'completed'"))
        if "latest_insight" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN latest_insight TEXT"))
        if "deadline" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN deadline TIMESTAMP"))
        if "location" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN location VARCHAR"))
        if "user_id" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN user_id VARCHAR"))
        if "user_email" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN user_email VARCHAR"))
        if "escalated" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN escalated BOOLEAN DEFAULT FALSE"))
        if "escalation_level" not in columns:
            connection.execute(text("ALTER TABLE grievance ADD COLUMN escalation_level INTEGER DEFAULT 0"))
        if "role" not in user_columns:
            connection.execute(text(f"ALTER TABLE user_account ADD COLUMN role VARCHAR DEFAULT '{settings.USER_DEFAULT_ROLE}'"))
        if "worker_backend" not in job_columns:
            connection.execute(text("ALTER TABLE complaint_job ADD COLUMN worker_backend VARCHAR DEFAULT 'local'"))
        if "task_ref" not in job_columns:
            connection.execute(text("ALTER TABLE complaint_job ADD COLUMN task_ref VARCHAR"))
        if "run_after" not in job_columns:
            connection.execute(text("ALTER TABLE complaint_job ADD COLUMN run_after TIMESTAMP"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_category ON grievance (category)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_location ON grievance (location)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_department ON grievance (department)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_user_id ON grievance (user_id)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_processing_status ON grievance (processing_status)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_embedding_key ON grievance (embedding_key)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_grievance_escalated ON grievance (escalated)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_job_worker_backend ON complaint_job (worker_backend)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_job_run_after ON complaint_job (run_after)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_user_role ON user_account (role)"))
