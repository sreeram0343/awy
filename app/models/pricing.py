import uuid
from datetime import datetime, date, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.variant import Variant


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("variants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    state_code: Mapped[str] = mapped_column(String(5), nullable=False, index=True)  # e.g., 'MH', 'DL', 'KA', 'TN'
    ex_showroom_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    variant: Mapped["Variant"] = relationship("Variant", back_populates="price_histories")

    __table_args__ = (
        Index("idx_price_history_variant_state_date", "variant_id", "state_code", "effective_date"),
    )

    def __repr__(self) -> str:
        return f"<PriceHistory id={self.id} variant_id={self.variant_id} state={self.state_code!r} price={self.ex_showroom_price}>"
