import json
from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlmodel import Session, select

from backend.config.settings import settings
from backend.models.grievance import Grievance
from backend.schemas.grievance import (
    AreaInsight,
    BottleneckResponse,
    ComplaintJobResponse,
    DashboardStats,
    HighPriorityComplaint,
    OwnedComplaint,
    RepeatedComplaint,
)
from backend.services.similarity import find_similar
from backend.services.sla import resolve_status
from backend.services.vector_store import vector_similar_texts


def save_complaint(db: Session, data: dict) -> Grievance:
    grievance = Grievance(**data)
    db.add(grievance)
    db.commit()
    db.refresh(grievance)
    return grievance


def check_repeated(db: Session, text: str, exclude_id: int | None = None) -> Grievance | None:
    stmt = select(Grievance).where(Grievance.complaint_text == text)
    if exclude_id is not None:
        stmt = stmt.where(Grievance.id != exclude_id)
    return db.exec(stmt).first()


def serialize_embedding(values: list[float]) -> str:
    return json.dumps(values)


def similarity_key_for_embedding(values: list[float], bucket_size: int = 4) -> str:
    if not values:
        return "empty"
    sliced = values[:bucket_size]
    return ":".join(f"{value:.2f}" for value in sliced)


def deserialize_embedding(raw_value: str | None) -> list[float]:
    if not raw_value:
        return []
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def get_similar_complaints(
    db: Session,
    complaint_text: str,
    embedding: list[float],
    category: str | None,
    location: str | None = None,
    limit: int = 3,
) -> list[str]:
    vector_matches = vector_similar_texts(
        db,
        embedding,
        category,
        location,
        min(limit, settings.SIMILARITY_CANDIDATE_LIMIT),
    )
    if vector_matches is not None:
        seen_vector: list[str] = []
        for matched_text in vector_matches:
            if matched_text != complaint_text and matched_text not in seen_vector:
                seen_vector.append(matched_text)
            if len(seen_vector) == limit:
                break
        return seen_vector

    statement = select(Grievance).where(Grievance.embedding.is_not(None))
    if category:
        statement = statement.where(Grievance.category == category)
    if location:
        statement = statement.where(
            (Grievance.location == location) | Grievance.location.is_(None)
        )
    embedding_key = similarity_key_for_embedding(embedding)
    if embedding_key != "empty":
        statement = statement.where(
            or_(Grievance.embedding_key == embedding_key, Grievance.embedding_key.is_(None))
        )
    statement = statement.order_by(Grievance.created_at.desc()).limit(settings.SIMILARITY_CANDIDATE_LIMIT)
    statements = db.exec(statement).all()
    stored_embeddings = [deserialize_embedding(item.embedding) for item in statements]
    stored_texts = [item.complaint_text for item in statements]
    matches = find_similar(embedding, stored_embeddings, stored_texts)

    similar: list[str] = []
    seen: set[str] = set()
    for matched_text in matches:
        if matched_text != complaint_text and matched_text not in seen:
            similar.append(matched_text)
            seen.add(matched_text)
        if len(similar) == limit:
            break
    return similar


def get_dashboard_stats(db: Session) -> DashboardStats:
    total = int(db.exec(select(func.count(Grievance.id))).one())

    categories = db.exec(
        select(Grievance.category, func.count()).group_by(Grievance.category)
    ).all()

    high = int(
        db.exec(select(func.count()).where(Grievance.urgency == "High")).one()
    )

    repeated = int(
        db.exec(select(func.count()).where(Grievance.is_repeated.is_(True))).one()
    )

    bottleneck_row = db.exec(
        select(Grievance.department, func.count())
        .group_by(Grievance.department)
        .order_by(func.count().desc())
    ).first()

    bottleneck = None
    bottleneck_count = 0
    if bottleneck_row:
        bottleneck = bottleneck_row[0] or "Unknown"
        bottleneck_count = int(bottleneck_row[1])

    return DashboardStats(
        total=total,
        categories={category or "Unknown": int(count) for category, count in categories},
        high_priority=high,
        repeated=repeated,
        bottleneck=bottleneck,
        bottleneck_count=bottleneck_count,
    )


def get_bottleneck(db: Session) -> BottleneckResponse:
    result = db.exec(
        select(Grievance.department, func.count())
        .group_by(Grievance.department)
        .order_by(func.count().desc())
    ).first()

    if not result:
        return BottleneckResponse(
            bottleneck="No data",
            reason="No complaints available yet",
            count=0,
        )

    department, count = result
    return BottleneckResponse(
        bottleneck=department or "Unknown",
        reason="Highest complaint load",
        complaints=int(count),
    )


def get_high_priority_complaints(db: Session) -> list[HighPriorityComplaint]:
    rows = db.exec(
        select(Grievance)
        .where(Grievance.urgency == "High")
        .order_by(Grievance.created_at.desc())
    ).all()

    return [
        HighPriorityComplaint(
            complaint_text=row.complaint_text,
            department=row.department,
            status=resolve_status(row.status, row.deadline),
            deadline=row.deadline,
            created_at=row.created_at,
        )
        for row in rows
    ]


def get_repeated_complaints(db: Session) -> list[RepeatedComplaint]:
    rows = db.exec(
        select(Grievance.complaint_text, func.count())
        .group_by(Grievance.complaint_text)
        .having(func.count() > 1)
        .order_by(func.count().desc())
    ).all()

    return [
        RepeatedComplaint(complaint_text=text, count=int(count))
        for text, count in rows
    ]


def get_area_insights(db: Session) -> list[AreaInsight]:
    rows = db.exec(
        select(Grievance.location, Grievance.category, func.count())
        .where(Grievance.location.is_not(None))
        .group_by(Grievance.location, Grievance.category)
        .order_by(func.count().desc())
    ).all()

    results: list[AreaInsight] = []
    for location, category, count in rows:
        if location and count >= 2:
            results.append(
                AreaInsight(
                    location=location,
                    issue=category or "Unknown",
                    count=int(count),
                    insight="Multiple users affected",
                )
            )
    return results


def get_owned_complaints(db: Session, user_id: str) -> list[OwnedComplaint]:
    rows = db.exec(
        select(Grievance)
        .where(Grievance.user_id == user_id)
        .order_by(Grievance.created_at.desc())
    ).all()
    return [
        OwnedComplaint(
            complaint_id=row.id or 0,
            complaint_text=row.complaint_text,
            category=row.category,
            urgency=row.urgency,
            department=row.department,
            status=row.status,
            processing_status=row.processing_status,
            escalated=row.escalated,
            escalation_level=row.escalation_level,
            created_at=row.created_at,
        )
        for row in rows
    ]
