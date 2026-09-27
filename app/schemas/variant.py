from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.spec import SpecResponse
from app.schemas.pricing import PriceHistoryResponse


class VariantBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    fuel_type: str = Field(description="Petrol, Diesel, EV, CNG, Hybrid")
    transmission: str = Field(description="Manual, Automatic, AMT, Single-Speed")
    engine_capacity_cc: Optional[float] = Field(default=None, ge=0.0)
    motor_power_kw: Optional[float] = Field(default=None, ge=0.0)
    battery_capacity_kwh: Optional[float] = Field(default=None, ge=0.0)
    is_active: bool = True


class VariantCreate(VariantBase):
    vehicle_id: UUID


class VariantResponse(VariantBase):
    id: UUID
    vehicle_id: UUID
    created_at: datetime
    updated_at: datetime
    spec: Optional[SpecResponse] = None
    price_histories: List[PriceHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)
