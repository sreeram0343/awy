from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class FilterConstraint(BaseModel):
    max_price: Optional[float] = Field(default=None, description="Maximum ex-showroom or on-road price ceiling")
    min_price: Optional[float] = Field(default=None, description="Minimum price floor")
    fuel_type: Optional[str] = Field(default=None, description="Petrol, Diesel, EV, CNG")
    abs_type: Optional[str] = Field(default=None, description="Single-Channel, Dual-Channel, etc.")
    min_ncap_rating: Optional[int] = Field(default=None, description="Minimum NCAP rating (e.g. 5)")
    min_airbags: Optional[int] = Field(default=None, description="Minimum number of airbags (e.g. 6)")
    body_type: Optional[str] = Field(default=None, description="SUV, Cruiser, Hatchback, Scooter, etc.")


class HybridSearchRequest(BaseModel):
    query: str = Field(min_length=1, description="Free text user query e.g. 'bikes with dual-channel ABS under 2L'")
    vehicle_type: Optional[str] = Field(default=None, description="'2W' or '4W'")
    filters: Optional[FilterConstraint] = None
    top_k: int = Field(default=10, ge=1, le=50)


class SearchMatchItem(BaseModel):
    chunk_id: str
    vehicle_id: str
    variant_id: Optional[str] = None
    vehicle_make: str
    vehicle_model: str
    topic: str
    content: str
    score: float
    metadata: Dict[str, Any]


class HybridSearchResponse(BaseModel):
    total_matches: int
    query: str
    applied_filters: Dict[str, Any]
    results: List[SearchMatchItem]
