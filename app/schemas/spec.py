from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SpecBase(BaseModel):
    seating_capacity: Optional[int] = Field(default=None, ge=1, le=10)
    mileage_kpl: Optional[float] = Field(default=None, ge=0.0)
    ev_range_km: Optional[float] = Field(default=None, ge=0.0)
    ncap_rating: Optional[int] = Field(default=None, ge=0, le=5)
    airbags_count: int = Field(default=2, ge=0)
    abs_type: Optional[str] = Field(default=None, description="Single-Channel, Dual-Channel, Cornering ABS, None")
    ground_clearance_mm: Optional[float] = Field(default=None, ge=0.0)
    length_mm: Optional[float] = Field(default=None, ge=0.0)
    width_mm: Optional[float] = Field(default=None, ge=0.0)
    height_mm: Optional[float] = Field(default=None, ge=0.0)
    wheelbase_mm: Optional[float] = Field(default=None, ge=0.0)
    boot_space_litres: Optional[float] = Field(default=None, ge=0.0)
    extra_features: Optional[Dict[str, Any]] = None


class SpecCreate(SpecBase):
    variant_id: UUID


class SpecResponse(SpecBase):
    id: UUID
    variant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
