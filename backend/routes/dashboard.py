from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.database.connection import get_session
from backend.schemas.grievance import (
    AreaInsight,
    BottleneckResponse,
    DashboardStats,
    HighPriorityComplaint,
    RepeatedComplaint,
)
from backend.services.auth import require_roles
from backend.services.db_service import (
    get_area_insights,
    get_bottleneck,
    get_dashboard_stats,
    get_high_priority_complaints,
    get_repeated_complaints,
)
from backend.services.observability import metrics


router = APIRouter(tags=["dashboard"])


@router.get("/health")
def health() -> dict[str, object]:
    snapshot = metrics.snapshot()
    return {
        "status": "ok",
        "worker_running": snapshot["gauges"].get("worker.running", 0) == 1,
        "app_started": snapshot["gauges"].get("app.started", 0) == 1,
    }


@router.get("/metrics")
def observability_metrics(
    _user=Depends(require_roles("admin", "staff")),
) -> dict[str, object]:
    return metrics.snapshot()


@router.get("/stats", response_model=DashboardStats)
def stats(
    db: Session = Depends(get_session),
    _user=Depends(require_roles("admin", "staff")),
) -> DashboardStats:
    return get_dashboard_stats(db)


@router.get("/high-priority", response_model=list[HighPriorityComplaint])
def high_priority(
    db: Session = Depends(get_session),
    _user=Depends(require_roles("admin", "staff")),
) -> list[HighPriorityComplaint]:
    return get_high_priority_complaints(db)


@router.get("/repeated", response_model=list[RepeatedComplaint])
def repeated(
    db: Session = Depends(get_session),
    _user=Depends(require_roles("admin", "staff")),
) -> list[RepeatedComplaint]:
    return get_repeated_complaints(db)


@router.get("/bottleneck", response_model=BottleneckResponse)
def bottleneck(
    db: Session = Depends(get_session),
    _user=Depends(require_roles("admin", "staff")),
) -> BottleneckResponse:
    return get_bottleneck(db)


@router.get("/area-insights", response_model=list[AreaInsight])
def area_insights(
    db: Session = Depends(get_session),
    _user=Depends(require_roles("admin", "staff")),
) -> list[AreaInsight]:
    return get_area_insights(db)
