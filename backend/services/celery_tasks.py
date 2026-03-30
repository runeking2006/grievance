from datetime import datetime, timezone

from sqlmodel import Session

from backend.database.connection import engine
from backend.models.grievance import Grievance
from backend.models.job import ComplaintJob
from backend.services.celery_app import celery_app
from backend.services.processing import enrich_grievance, process_grievance_escalation
from backend.services.queue import ensure_escalation_job


if celery_app is not None:

    @celery_app.task(name="backend.enrich_complaint")
    def enrich_complaint_task(job_id: int) -> None:
        with Session(engine) as session:
            job = session.get(ComplaintJob, job_id)
            if job is None:
                return
            grievance = session.get(Grievance, job.grievance_id)
            if grievance is None:
                job.status = "failed"
                job.error_message = "Complaint not found"
                job.updated_at = datetime.now(timezone.utc)
                session.add(job)
                session.commit()
                return

            try:
                job.status = "processing"
                job.attempts += 1
                job.updated_at = datetime.now(timezone.utc)
                session.add(job)
                session.commit()
                session.refresh(job)

                if job.job_type == "enrich_complaint":
                    enrich_grievance(session, grievance)
                    ensure_escalation_job(session, grievance)
                elif job.job_type == "sla_escalation":
                    process_grievance_escalation(grievance)
                job.status = "completed"
                job.updated_at = datetime.now(timezone.utc)
                session.add(grievance)
                session.add(job)
                session.commit()
            except Exception as exc:
                session.rollback()
                failed_job = session.get(ComplaintJob, job_id)
                failed_grievance = session.get(Grievance, job.grievance_id)
                if failed_job:
                    failed_job.status = "failed"
                    failed_job.error_message = str(exc)
                    failed_job.updated_at = datetime.now(timezone.utc)
                    session.add(failed_job)
                if failed_grievance:
                    failed_grievance.processing_status = "failed"
                    session.add(failed_grievance)
                session.commit()
