from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.variant import VariantResponse


class VehicleBase(BaseModel):
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    category: str = Field(description="'4W' or '2W'")
    body_type: str = Field(description="e.g. SUV, Hatchback, Cruiser, Scooter")


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    variants: List[VariantResponse] = []

    model_config = ConfigDict(from_attributes=True)


class VehicleSpecDetailResponse(BaseModel):
    id: UUID
    make: str
    model: str
    category: str
    body_type: str
    variants: List[VariantResponse]

    model_config = ConfigDict(from_attributes=True)
