import asyncio

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlmodel import Session

from backend.database.connection import engine, get_session
from backend.models.grievance import Grievance
from backend.models.job import ComplaintJob
from backend.schemas.grievance import ComplaintCreate, ComplaintJobResponse, ComplaintResponse, OwnedComplaint
from backend.services.auth import (
    decode_access_token,
    get_optional_user,
    get_user_by_api_key,
    get_user_by_id,
    require_user,
)
from backend.services.ai_pipeline import process
from backend.services.db_service import (
    check_repeated,
    get_owned_complaints,
    get_similar_complaints,
    save_complaint,
    serialize_embedding,
    similarity_key_for_embedding,
)
from backend.services.notification import send_notification
from backend.services.queue import enqueue_job, ensure_escalation_job, fetch_job
from backend.services.rag import generate_rag_insight
from backend.services.routing import route
from backend.services.sla import compute_deadline


router = APIRouter(tags=["complaints"])


def _validate_job_access(db: Session, job_id: int, user_id: str, user_role: str) -> ComplaintJob:
    job = fetch_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    grievance = db.get(Grievance, job.grievance_id)
    if grievance is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if user_role not in {"admin", "staff"} and grievance.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to view this job")
    return job


@router.post("/complaint", response_model=ComplaintResponse)
def create_complaint(
    data: ComplaintCreate,
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
) -> ComplaintResponse:
    result = process(data.text)
    department = route(result["category"])
    existing = check_repeated(db, data.text)
    similar_complaints = get_similar_complaints(
        db,
        data.text,
        result["embedding"],
        result["category"],
        data.location,
    )

    record = {
        "complaint_text": data.text,
        "translated_text": result.get("translated_text"),
        "category": result["category"],
        "urgency": result["urgency"],
        "embedding": serialize_embedding(result["embedding"]),
        "embedding_key": similarity_key_for_embedding(result["embedding"]),
        "department": department,
        "language": result.get("language"),
        "location": data.location,
        "user_id": user.id if user else None,
        "user_email": user.email if user else None,
        "is_repeated": existing is not None,
        "status": "Pending",
        "processing_status": "completed",
        "deadline": compute_deadline(result["urgency"]),
    }

    saved = save_complaint(db, record)
    from backend.services.vector_store import save_vector_embedding
    if saved.id is not None:
        save_vector_embedding(db, saved.id, result["embedding"])
    insight = "Repeated issue detected" if saved.is_repeated else "New issue"
    if similar_complaints:
        insight = generate_rag_insight(
            complaint_text=data.text,
            category=saved.category or "General",
            similar_complaints=similar_complaints,
            urgency=saved.urgency,
            department=saved.department,
            location=saved.location,
        )
    saved.latest_insight = insight
    db.add(saved)
    db.commit()
    db.refresh(saved)
    ensure_escalation_job(db, saved)
    send_notification(
        saved.user_email,
        f"Complaint received. Status: {saved.status}. Deadline: {saved.deadline.isoformat() if saved.deadline else 'Not assigned'}.",
    )

    return ComplaintResponse(
        complaint_id=saved.id,
        category=saved.category or "General",
        urgency=saved.urgency or "Low",
        department=saved.department or "Admin",
        insight=insight,
        status=saved.status,
        deadline=saved.deadline,
        similar_complaints=similar_complaints,
        processing_status=saved.processing_status,
        owner_id=saved.user_id,
        escalated=saved.escalated,
        escalation_level=saved.escalation_level,
    )


@router.post("/complaint/async", response_model=ComplaintJobResponse)
def create_complaint_async(
    data: ComplaintCreate,
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
) -> ComplaintJobResponse:
    grievance = save_complaint(
        db,
        {
            "complaint_text": data.text,
            "location": data.location,
            "user_id": user.id if user else None,
            "user_email": user.email if user else None,
            "status": "Queued",
            "processing_status": "queued",
            "latest_insight": "Queued for background enrichment",
        },
    )
    job = enqueue_job(db, grievance.id or 0)
    send_notification(
        grievance.user_email,
        "Complaint received and queued for background processing.",
    )
    return ComplaintJobResponse(
        job_id=job.id or 0,
        grievance_id=grievance.id or 0,
        status=job.status,
        job_type=job.job_type,
        error_message=job.error_message,
    )


@router.get("/jobs/{job_id}", response_model=ComplaintJobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_session),
    user=Depends(require_user),
) -> ComplaintJobResponse:
    job = _validate_job_access(db, job_id, user.id, user.role)
    return ComplaintJobResponse(
        job_id=job.id or 0,
        grievance_id=job.grievance_id,
        status=job.status,
        job_type=job.job_type,
        error_message=job.error_message,
    )


@router.get("/my-complaints", response_model=list[OwnedComplaint])
def my_complaints(
    db: Session = Depends(get_session),
    user=Depends(require_user),
) -> list[OwnedComplaint]:
    return get_owned_complaints(db, user.id)


@router.websocket("/ws/jobs/{job_id}")
async def job_updates(websocket: WebSocket, job_id: int) -> None:
    token = websocket.query_params.get("token")
    api_key = websocket.query_params.get("api_key")

    with Session(engine) as db:
        user = None
        if token:
            payload = decode_access_token(token)
            user = get_user_by_id(db, payload["sub"])
        elif api_key:
            user = get_user_by_api_key(db, api_key)

        if user is None or not user.is_active:
            await websocket.close(code=4401, reason="Authentication required")
            return

        try:
            job = _validate_job_access(db, job_id, user.id, user.role)
        except HTTPException as exc:
            code = 4404 if exc.status_code == 404 else 4403
            await websocket.close(code=code, reason=exc.detail)
            return

    await websocket.accept()

    while True:
        with Session(engine) as db:
            try:
                job = _validate_job_access(db, job_id, user.id, user.role)
            except HTTPException as exc:
                await websocket.send_json({"error": exc.detail, "status": "failed"})
                await websocket.close(code=4404 if exc.status_code == 404 else 4403)
                return

            await websocket.send_json(
                {
                    "job_id": job.id or 0,
                    "grievance_id": job.grievance_id,
                    "status": job.status,
                    "job_type": job.job_type,
                    "error_message": job.error_message,
                }
            )
            if job.status in {"completed", "failed"}:
                await websocket.close(code=1000)
                return
        await asyncio.sleep(1.2)
