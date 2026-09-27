from datetime import datetime, timezone
from typing import Dict, Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class MetaEnvelope(BaseModel):
    source_version: str = Field(default="v1.0.0", description="Data / system source version")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when response was generated"
    )

class APIEnvelope(BaseModel, Generic[T]):
    status: str = Field(default="success", description="Status string ('success' or 'error')")
    data: T
    meta: MetaEnvelope = Field(default_factory=MetaEnvelope)

class DatabaseHealth(BaseModel):
    status: str
    engine: str
    latency_ms: float
    error: Optional[str] = None

class QdrantHealth(BaseModel):
    status: str
    host: str
    port: int
    collection_exists: bool
    collections: Optional[list[str]] = None
    error: Optional[str] = None

class SystemHealthData(BaseModel):
    app_name: str
    environment: str
    database: DatabaseHealth
    qdrant: QdrantHealth
    overall_status: str
