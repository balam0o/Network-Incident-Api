from datetime import datetime

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