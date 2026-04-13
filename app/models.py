from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hostname: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), unique=True, nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    environment: Mapped[str] = mapped_column(String(50), nullable=False, default="production")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)