from datetime import datetime, timezone
from typing import Optional, Literal, Dict, Any, List
from pydantic import BaseModel, Field


class VoiceSessionCreate(BaseModel):
    language: Literal["en", "ml"] = Field("en", description="Primary conversation language (English or Malayalam)")
    dealership_id: Optional[str] = Field("apex-kerala-01", description="Identifier of the dealership")
    customer_name: Optional[str] = Field(None, description="Optional customer display name")


class VoiceSessionResponse(BaseModel):
    session_id: str
    language: str
    sample_rate: int = 16000
    websocket_url: str
    status: str = "initialized"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VoiceTextRequest(BaseModel):
    session_id: str
    text: str
    language: Literal["en", "ml"] = "en"


class ToolExecutionTrace(BaseModel):
    tool_name: str
    status: str = "success"
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    output_summary: str
    latency_ms: float = 24.5


class VoiceTextResponse(BaseModel):
    session_id: str
    user_text: str
    response_text: str
    audio_base64: Optional[str] = None
    language: str
    recommended_vehicles: Optional[List[Dict[str, Any]]] = None
    state: str = "idle"
    tool_executed: Optional[ToolExecutionTrace] = None
    session_memory: Optional[Dict[str, Any]] = None


class FeedbackCreate(BaseModel):
    session_id: Optional[str] = None
    query: str
    response_text: str
    rating: Literal["positive", "negative"]
    category: Optional[str] = "accuracy"
    notes: Optional[str] = None
    language: str = "en"
