from datetime import datetime, timezone
from threading import Event, Thread
from time import sleep

from sqlmodel import Session, select

from backend.config.settings import settings
from backend.database.connection import engine
from backend.models.grievance import Grievance
from backend.models.job import ComplaintJob
from backend.services.celery_app import celery_app
from backend.services.processing import enrich_grievance, process_grievance_escalation
from backend.services.observability import metrics, queue_logger, timed


_stop_event = Event()
_worker_thread: Thread | None = None


def enqueue_job(
    session: Session,
    grievance_id: int,
    job_type: str = "enrich_complaint",
    run_after: datetime | None = None,
) -> ComplaintJob:
    metrics.increment("jobs.enqueued")
    backend = "celery" if settings.USE_DISTRIBUTED_QUEUE and celery_app is not None else "local"
    job = ComplaintJob(
        grievance_id=grievance_id,
        job_type=job_type,
        status="queued",
        worker_backend=backend,
        run_after=run_after,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    if backend == "celery" and celery_app is not None:
        task_kwargs = {}
        if run_after is not None:
            task_kwargs["eta"] = run_after
        async_result = celery_app.send_task("backend.enrich_complaint", args=[job.id], **task_kwargs)
        job.task_ref = async_result.id
        session.add(job)
        session.commit()
        session.refresh(job)
        queue_logger.info(
            "job_dispatched",
            extra={
                "extra_fields": {
                    "job_id": job.id,
                    "job_type": job.job_type,
                    "worker_backend": job.worker_backend,
                    "task_ref": job.task_ref,
                }
            },
        )
    return job


def ensure_escalation_job(session: Session, grievance: Grievance) -> ComplaintJob | None:
    if grievance.id is None or grievance.deadline is None:
        return None

    existing = session.exec(
        select(ComplaintJob)
        .where(ComplaintJob.grievance_id == grievance.id)
        .where(ComplaintJob.job_type == "sla_escalation")
        .where(ComplaintJob.status.in_(["queued", "processing"]))
    ).first()
    if existing:
        return existing

    return enqueue_job(
        session,
        grievance_id=grievance.id,
        job_type="sla_escalation",
        run_after=grievance.deadline,
    )


def fetch_job(session: Session, job_id: int) -> ComplaintJob | None:
    return session.get(ComplaintJob, job_id)


def _mark_job(job: ComplaintJob, status: str, error_message: str | None = None) -> None:
    job.status = status
    job.error_message = error_message
    job.updated_at = datetime.now(timezone.utc)


def _work_once() -> None:
    with timed("jobs.worker_cycle"), Session(engine) as session:
        job = session.exec(
            select(ComplaintJob)
            .where(ComplaintJob.status == "queued")
            .where(ComplaintJob.worker_backend == "local")
            .where((ComplaintJob.run_after.is_(None)) | (ComplaintJob.run_after <= datetime.now(timezone.utc)))
            .order_by(ComplaintJob.created_at.asc())
        ).first()
        if job is None:
            return

        queue_logger.info(
            "job_started",
            extra={"extra_fields": {"job_id": job.id, "job_type": job.job_type}},
        )
        metrics.increment("jobs.started")
        job.status = "processing"
        job.attempts += 1
        job.updated_at = datetime.now(timezone.utc)
        session.add(job)
        session.commit()
        session.refresh(job)

        try:
            grievance = None
            if job.job_type == "enrich_complaint":
                grievance = session.get(Grievance, job.grievance_id)
                if grievance is None:
                    raise ValueError("Complaint not found")
                enrich_grievance(session, grievance)
                ensure_escalation_job(session, grievance)
            elif job.job_type == "sla_escalation":
                grievance = session.get(Grievance, job.grievance_id)
                if grievance is None:
                    raise ValueError("Complaint not found")
                process_grievance_escalation(grievance)
            _mark_job(job, "completed")
            if grievance is not None:
                session.add(grievance)
            session.add(job)
            session.commit()
            metrics.increment("jobs.completed")
            queue_logger.info(
                "job_completed",
                extra={"extra_fields": {"job_id": job.id, "job_type": job.job_type}},
            )
        except Exception as exc:
            session.rollback()
            metrics.increment("jobs.failed")
            queue_logger.exception(
                "job_failed",
                extra={"extra_fields": {"job_id": job.id, "job_type": job.job_type}},
            )
            with Session(engine) as retry_session:
                retry_job = retry_session.get(ComplaintJob, job.id)
                if retry_job:
                    _mark_job(retry_job, "failed", str(exc))
                    grievance = retry_session.get(Grievance, retry_job.grievance_id)
                    if grievance:
                        grievance.processing_status = "failed"
                    retry_session.add(retry_job)
                    retry_session.commit()

def _worker_loop(poll_interval: float) -> None:
    while not _stop_event.is_set():
        _work_once()
        sleep(poll_interval)


def start_worker(poll_interval: float = 2.0) -> None:
    global _worker_thread
    if _worker_thread is not None and _worker_thread.is_alive():
        return
    _stop_event.clear()
    _worker_thread = Thread(target=_worker_loop, args=(poll_interval,), daemon=True)
    _worker_thread.start()
    queue_logger.info(
        "worker_started",
        extra={"extra_fields": {"poll_interval_seconds": poll_interval}},
    )
    metrics.set_gauge("worker.running", 1)


def stop_worker() -> None:
    _stop_event.set()
    metrics.set_gauge("worker.running", 0)
    queue_logger.info("worker_stopped")
