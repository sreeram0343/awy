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


class VoiceTextResponse(BaseModel):
    session_id: str
    user_text: str
    response_text: str
    audio_base64: Optional[str] = None
    language: str
    recommended_vehicles: Optional[List[Dict[str, Any]]] = None
    state: str = "idle"
