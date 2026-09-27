import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.variant import Variant
    from app.models.review import Review


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    make: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # '4W' or '2W'
    body_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., 'SUV', 'Cruiser', 'Hatchback'

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    variants: Mapped[List["Variant"]] = relationship("Variant", back_populates="vehicle", cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="vehicle", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("make", "model", name="uq_vehicle_make_model"),
    )

    def __repr__(self) -> str:
        return f"<Vehicle id={self.id} make={self.make!r} model={self.model!r} category={self.category!r}>"
