"""Modèle ORM d'alerte et enum de sévérité."""

from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AlertLevel(StrEnum):
    """Niveau de sévérité métier dérivé des seuils."""
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"),
        index=True,
    )
    level: Mapped[AlertLevel] = mapped_column(
        Enum(AlertLevel, name="alert_level", native_enum=False),
        index=True,
    )
    message: Mapped[str] = mapped_column(String(255))
    # `is_active=False` signifie que l'alerte reste dans l'historique mais n'est plus ouverte.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    machine = relationship("Machine", back_populates="alerts")
