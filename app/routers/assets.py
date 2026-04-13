from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Asset
from app.schemas import AssetCreate, AssetRead, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    existing_asset = db.scalar(
        select(Asset).where(
            or_(
                Asset.hostname == payload.hostname,
                Asset.ip_address == payload.ip_address,
            )
        )
    )

    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hostname or IP already exists",
        )

    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/", response_model=list[AssetRead])
def list_assets(db: Session = Depends(get_db)):
    assets = db.scalars(
        select(Asset).order_by(Asset.created_at.desc())
    ).all()
    return assets


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    data = payload.model_dump(exclude_unset=True)

    if "hostname" in data and data["hostname"] != asset.hostname:
        existing_hostname = db.scalar(
            select(Asset).where(Asset.hostname == data["hostname"])
        )
        if existing_hostname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hostname already exists",
            )

    if "ip_address" in data and data["ip_address"] != asset.ip_address:
        existing_ip = db.scalar(
            select(Asset).where(Asset.ip_address == data["ip_address"])
        )
        if existing_ip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IP already exists",
            )

    for field, value in data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted"}