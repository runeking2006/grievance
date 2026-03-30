from datetime import datetime, timedelta, timezone


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def compute_deadline(urgency: str, created_at: datetime | None = None) -> datetime:
    base_time = created_at or datetime.now(timezone.utc)
    offsets = {
        "High": timedelta(hours=24),
        "Medium": timedelta(hours=48),
        "Low": timedelta(hours=72),
    }
    return base_time + offsets.get(urgency, timedelta(hours=48))


def resolve_status(current_status: str, deadline: datetime | None, now: datetime | None = None) -> str:
    if current_status == "Resolved":
        return current_status
    if deadline is None:
        return current_status
    reference_time = _as_utc(now or datetime.now(timezone.utc))
    normalized_deadline = _as_utc(deadline)
    return "Delayed" if reference_time > normalized_deadline else current_status


def check_escalation(grievance, now: datetime | None = None):
    if grievance.deadline is None or grievance.status == "Resolved":
        return grievance

    reference_time = _as_utc(now or datetime.now(timezone.utc))
    deadline = _as_utc(grievance.deadline)
    if reference_time > deadline and grievance.status != "Escalated":
        grievance.escalated = True
        grievance.escalation_level += 1
        grievance.status = "Escalated"
    return grievance
