from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class LeadCreate(BaseModel):
    variant_id: UUID
    user_name: str = Field(min_length=2, max_length=100)
    user_email: str = Field(description="User contact email")
    user_phone: str = Field(min_length=10, max_length=15)
    state_code: str = Field(min_length=2, max_length=5)
    dealership_id: str = Field(min_length=1, max_length=50)
    computed_on_road_price: float = Field(gt=0.0)
    consent_given: bool = Field(description="Must be True for PII submission consent")


class LeadResponse(BaseModel):
    id: UUID
    variant_id: UUID
    user_name: str
    user_email: str
    user_phone: str
    state_code: str
    dealership_id: str
    computed_on_road_price: float
    status: str
    consent_given: bool
    consent_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
