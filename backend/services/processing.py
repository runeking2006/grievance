from sqlmodel import Session

from backend.models.grievance import Grievance
from backend.services.ai_pipeline import process
from backend.services.db_service import (
    check_repeated,
    get_similar_complaints,
    serialize_embedding,
    similarity_key_for_embedding,
)
from backend.services.notification import send_notification
from backend.services.rag import generate_rag_insight
from backend.services.routing import route
from backend.services.sla import check_escalation, compute_deadline
from backend.services.vector_store import save_vector_embedding


def enrich_grievance(session: Session, grievance: Grievance) -> None:
    result = process(grievance.complaint_text)
    grievance.category = result["category"]
    grievance.urgency = result["urgency"]
    grievance.embedding = serialize_embedding(result["embedding"])
    grievance.embedding_key = similarity_key_for_embedding(result["embedding"])
    grievance.department = route(result["category"])
    grievance.translated_text = result.get("translated_text")
    grievance.language = result.get("language")
    grievance.is_repeated = check_repeated(
        session,
        grievance.complaint_text,
        exclude_id=grievance.id,
    ) is not None
    grievance.status = "Pending"
    grievance.deadline = compute_deadline(result["urgency"])

    if grievance.id is not None:
        save_vector_embedding(session, grievance.id, result["embedding"])

    similar = get_similar_complaints(
        session,
        grievance.complaint_text,
        result["embedding"],
        grievance.category,
        grievance.location,
    )
    grievance.latest_insight = (
        generate_rag_insight(
            complaint_text=grievance.complaint_text,
            category=grievance.category or "General",
            similar_complaints=similar,
            urgency=grievance.urgency or "Low",
            department=grievance.department or "Admin",
            location=grievance.location,
        )
        if similar
        else ("Repeated issue detected" if grievance.is_repeated else "New issue")
    )
    grievance.processing_status = "completed"
    send_notification(
        grievance.user_email,
        f"Complaint processed. Status: {grievance.status}. Department: {grievance.department or 'Admin'}.",
    )


def process_grievance_escalation(grievance: Grievance) -> bool:
    previous_status = grievance.status
    previous_level = grievance.escalation_level
    check_escalation(grievance)
    changed = (
        grievance.status != previous_status
        or grievance.escalation_level != previous_level
    )
    if changed:
        send_notification(
            grievance.user_email,
            "Your complaint has been escalated due to delay.",
        )
    return changed
