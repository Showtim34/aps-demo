"""Modèle ORM de mesure.

Une mesure correspond à la télémétrie brute envoyée pour une machine.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"),
        index=True,
    )
    # Ces valeurs sont volontairement stockées en `float` simples pour garder
    # la démo lisible. Un projet plus avancé pourrait introduire des unités ou
    # des objets valeur.
    temperature: Mapped[float]
    vibration: Mapped[float]
    power: Mapped[float]
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )

    machine = relationship("Machine", back_populates="measurements")
