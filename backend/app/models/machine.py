"""Modèle ORM de machine et enum d'état."""

from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MachineStatus(StrEnum):
    """État opérationnel d'une machine tel qu'exposé par l'API."""
    IDLE = "idle"
    RUNNING = "running"
    ALERT = "alert"
    MAINTENANCE = "maintenance"


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Clé étrangère vers le site parent.
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), index=True)
    # Les codes machine sont uniques car ils servent d'identifiants métier.
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    machine_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[MachineStatus] = mapped_column(
        Enum(MachineStatus, name="machine_status", native_enum=False),
        default=MachineStatus.IDLE,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    site = relationship("Site", back_populates="machines")
    # `order_by` signifie que les mesures reviennent de la plus récente à la
    # plus ancienne quand on charge cette relation.
    measurements = relationship(
        "Measurement",
        back_populates="machine",
        cascade="all, delete-orphan",
        order_by="desc(Measurement.recorded_at)",
    )
    alerts = relationship("Alert", back_populates="machine", cascade="all, delete-orphan")
