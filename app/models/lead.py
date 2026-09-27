import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.variant import Variant


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("variants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_email: Mapped[str] = mapped_column(String(100), nullable=False)
    user_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    state_code: Mapped[str] = mapped_column(String(5), nullable=False)
    dealership_id: Mapped[str] = mapped_column(String(50), nullable=False)
    computed_on_road_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Lead Status Workflow: created -> sent -> acknowledged -> converted / failed
    status: Mapped[str] = mapped_column(String(30), default="created", nullable=False, index=True)
    
    # Explicit Consent Tracking
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    variant: Mapped["Variant"] = relationship("Variant", back_populates="leads")

    __table_args__ = (
        Index("idx_leads_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Lead id={self.id} user={self.user_name!r} status={self.status!r}>"
