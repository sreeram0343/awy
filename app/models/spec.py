import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.variant import Variant


class Spec(Base):
    __tablename__ = "specs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("variants.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    seating_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mileage_kpl: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    ev_range_km: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    ncap_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    airbags_count: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    abs_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # Single-Channel, Dual-Channel, None
    ground_clearance_mm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    length_mm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    width_mm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    height_mm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    wheelbase_mm: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    boot_space_litres: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    
    # Flexible JSON storage for extensible features (sunroof, ventilated seats, etc.)
    extra_features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    variant: Mapped["Variant"] = relationship("Variant", back_populates="spec")

    def __repr__(self) -> str:
        return f"<Spec id={self.id} variant_id={self.variant_id} abs={self.abs_type!r}>"
