from datetime import datetime
from app.models import IncidentSeverity, IncidentStatus
from pydantic import BaseModel, ConfigDict, Field


class AssetCreate(BaseModel):
    hostname: str = Field(min_length=2, max_length=100)
    ip_address: str = Field(min_length=7, max_length=45)
    owner: str = Field(min_length=2, max_length=100)
    environment: str = Field(default="production", min_length=2, max_length=50)


class AssetUpdate(BaseModel):
    hostname: str | None = Field(default=None, min_length=2, max_length=100)
    ip_address: str | None = Field(default=None, min_length=7, max_length=45)
    owner: str | None = Field(default=None, min_length=2, max_length=100)
    environment: str | None = Field(default=None, min_length=2, max_length=50)


class AssetRead(BaseModel):
    id: int
    hostname: str
    ip_address: str
    owner: str
    environment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=5)
    severity: IncidentSeverity
    asset_id: int

class IncidentRead(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    asset_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=5)
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    asset_id: int | None = None