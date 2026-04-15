from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Incident, IncidentSeverity, IncidentStatus, User
from app.schemas import StatsSummary

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_incidents = db.scalar(select(func.count()).select_from(Incident)) or 0

    open_incidents = db.scalar(
        select(func.count()).select_from(Incident).where(
            Incident.status == IncidentStatus.open.value
        )
    ) or 0

    in_progress_incidents = db.scalar(
        select(func.count()).select_from(Incident).where(
            Incident.status == IncidentStatus.in_progress.value
        )
    ) or 0

    closed_incidents = db.scalar(
        select(func.count()).select_from(Incident).where(
            Incident.status == IncidentStatus.closed.value
        )
    ) or 0

    critical_incidents = db.scalar(
        select(func.count()).select_from(Incident).where(
            Incident.severity == IncidentSeverity.critical.value
        )
    ) or 0

    return StatsSummary(
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        in_progress_incidents=in_progress_incidents,
        closed_incidents=closed_incidents,
        critical_incidents=critical_incidents,
    )