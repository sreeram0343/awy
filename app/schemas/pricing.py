from typing import Optional
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class PriceHistoryBase(BaseModel):
    state_code: str = Field(min_length=2, max_length=5, description="State code e.g. MH, DL, KA")
    ex_showroom_price: float = Field(gt=0.0, description="Ex-showroom price in INR")
    effective_date: date
    source_version: str = "v1.0"


class PriceHistoryCreate(PriceHistoryBase):
    variant_id: UUID


class PriceHistoryResponse(PriceHistoryBase):
    id: UUID
    variant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
