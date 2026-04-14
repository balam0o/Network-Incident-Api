from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Asset, Incident, IncidentSeverity, IncidentStatus, User
from app.schemas import IncidentCreate, IncidentRead, IncidentUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.get(Asset, payload.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if payload.assigned_to is not None:
        assigned_user = db.get(User, payload.assigned_to)
        if not assigned_user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity.value,
        status=IncidentStatus.open.value,
        asset_id=payload.asset_id,
        created_by=current_user.id,
        assigned_to=payload.assigned_to,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/", response_model=list[IncidentRead])
def list_incidents(
    severity: IncidentSeverity | None = Query(default=None),
    status_filter: IncidentStatus | None = Query(default=None, alias="status"),
    asset_id: int | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Incident)

    if severity:
        stmt = stmt.where(Incident.severity == severity.value)

    if status_filter:
        stmt = stmt.where(Incident.status == status_filter.value)

    if asset_id is not None:
        stmt = stmt.where(Incident.asset_id == asset_id)

    stmt = stmt.order_by(Incident.created_at.desc()).offset(skip).limit(limit)

    incidents = db.scalars(stmt).all()
    return incidents


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    data = payload.model_dump(exclude_unset=True)

    if "severity" in data and data["severity"] is not None:
        data["severity"] = data["severity"].value

    if "status" in data and data["status"] is not None:
        data["status"] = data["status"].value

    if "asset_id" in data and data["asset_id"] is not None:
        asset = db.get(Asset, data["asset_id"])
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

    if "assigned_to" in data and data["assigned_to"] is not None:
        assigned_user = db.get(User, data["assigned_to"])
        if not assigned_user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    for field, value in data.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/{incident_id}")
def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    db.delete(incident)
    db.commit()
    return {"message": "Incident deleted"}