import uuid
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Numeric, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.spec import Spec
    from app.models.pricing import PriceHistory
    from app.models.review import Review
    from app.models.lead import Lead


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    fuel_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # Petrol, Diesel, EV, CNG, Hybrid
    transmission: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # Manual, Automatic, AMT, Single-Speed
    engine_capacity_cc: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    motor_power_kw: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    battery_capacity_kwh: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="variants")
    spec: Mapped[Optional["Spec"]] = relationship("Spec", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    price_histories: Mapped[List["PriceHistory"]] = relationship("PriceHistory", back_populates="variant", cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="variant")
    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="variant")

    __table_args__ = (
        UniqueConstraint("vehicle_id", "name", name="uq_variant_vehicle_name"),
    )

    def __repr__(self) -> str:
        return f"<Variant id={self.id} name={self.name!r} fuel={self.fuel_type!r}>"
