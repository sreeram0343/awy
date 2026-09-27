import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.variant import Variant


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("variants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    topic: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # performance, comfort, reliability, service_cost
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    chunk_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)  # SHA-256 for idempotency
    vector_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Qdrant Point ID
    source_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="reviews")
    variant: Mapped[Optional["Variant"]] = relationship("Variant", back_populates="reviews")

    __table_args__ = (
        Index("idx_review_vehicle_topic", "vehicle_id", "topic"),
    )

    def __repr__(self) -> str:
        return f"<Review id={self.id} vehicle_id={self.vehicle_id} topic={self.topic!r}>"
