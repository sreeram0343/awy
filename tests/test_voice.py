import pytest
import io
import wave
import base64
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.voice_service import voice_service


@pytest.mark.asyncio
async def test_voice_session_creation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/voice/session", json={"language": "en", "dealership_id": "apex-kerala-01"})
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "session_id" in data["data"]
        assert data["data"]["language"] == "en"
        assert "/api/v1/voice/stream/" in data["data"]["websocket_url"]


@pytest.mark.asyncio
async def test_voice_text_fallback_english():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create session first
        sess_resp = await ac.post("/api/v1/voice/session", json={"language": "en"})
        session_id = sess_resp.json()["data"]["session_id"]

        # Send typed query
        response = await ac.post("/api/v1/voice/text", json={
            "session_id": session_id,
            "text": "Hello, I am looking for a reliable petrol SUV with 5-star safety.",
            "language": "en"
        })
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["session_id"] == session_id
        assert len(data["response_text"]) > 10
        assert data["audio_base64"] is not None
        assert len(data["recommended_vehicles"]) > 0

        # Verify returned audio is a valid WAV container
        raw_wav = base64.b64decode(data["audio_base64"])
        with wave.open(io.BytesIO(raw_wav), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 16000


@pytest.mark.asyncio
async def test_voice_text_fallback_malayalam():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        sess_resp = await ac.post("/api/v1/voice/session", json={"language": "ml"})
        session_id = sess_resp.json()["data"]["session_id"]

        response = await ac.post("/api/v1/voice/text", json={
            "session_id": session_id,
            "text": "നമസ്കാരം, എനിക്ക് നല്ലൊരു ഇലക്ട്രിക് കാർ വേണം",
            "language": "ml"
        })
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["session_id"] == session_id
        assert len(data["response_text"]) > 0
        assert data["audio_base64"] is not None


def test_speech_wav_cadence_generator():
    wav_bytes = voice_service.generate_speech_wav("Hello Apex Motors", sample_rate=16000)
    assert len(wav_bytes) > 44
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"
