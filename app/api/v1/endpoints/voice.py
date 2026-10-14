import json
import base64
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from app.schemas.health import APIEnvelope
from app.schemas.voice import VoiceSessionCreate, VoiceSessionResponse, VoiceTextRequest, VoiceTextResponse
from app.services.voice_service import voice_service
from app.core.logging import logger

router = APIRouter()


@router.post("/session", response_model=APIEnvelope[VoiceSessionResponse])
async def create_voice_session(payload: VoiceSessionCreate):
    """
    Initializes a voice session with language configuration and returns WebSocket URL.
    """
    session = voice_service.create_session(
        language=payload.language,
        dealership_id=payload.dealership_id or "apex-kerala-01"
    )
    resp = VoiceSessionResponse(
        session_id=session.session_id,
        language=session.language,
        sample_rate=16000,
        websocket_url=f"/api/v1/voice/stream/{session.session_id}",
        status="ready"
    )
    return APIEnvelope[VoiceSessionResponse](data=resp)


@router.post("/text", response_model=APIEnvelope[VoiceTextResponse])
async def text_query_fallback(payload: VoiceTextRequest):
    """
    Typed fallback endpoint that returns answer, vehicle recommendations, and audio synthesis.
    """
    response_text, recommended_vehicles = await voice_service.process_user_intent(
        text=payload.text,
        language=payload.language
    )
    
    # Synthesize audio for the response
    wav_bytes = voice_service.generate_speech_wav(response_text)
    audio_b64 = base64.b64encode(wav_bytes).decode("ascii")

    res = VoiceTextResponse(
        session_id=payload.session_id,
        user_text=payload.text,
        response_text=response_text,
        audio_base64=audio_b64,
        language=payload.language,
        recommended_vehicles=recommended_vehicles,
        state="idle"
    )
    return APIEnvelope[VoiceTextResponse](data=res)


@router.websocket("/stream/{session_id}")
async def voice_websocket_stream(websocket: WebSocket, session_id: str):
    """
    Bidirectional streaming WebSocket for real-time audio input, speech output, and state synchronization.
    """
    await websocket.accept()
    session = voice_service.get_session(session_id)
    if not session:
        session = voice_service.create_session(language="en")
    
    session.websocket = websocket
    session.state = "listening"

    try:
        await websocket.send_json({
            "type": "state_change",
            "state": "listening",
            "language": session.language
        })

        while True:
            raw_msg = await websocket.receive_text()
            try:
                data = json.loads(raw_msg)
            except Exception:
                continue

            msg_type = data.get("type")

            if msg_type == "interrupt":
                session.is_interrupted = True
                session.state = "interrupted"
                await websocket.send_json({
                    "type": "state_change",
                    "state": "interrupted"
                })
                await asyncio.sleep(0.1)
                session.state = "listening"
                await websocket.send_json({
                    "type": "state_change",
                    "state": "listening"
                })

            elif msg_type == "text_input":
                user_text = data.get("text", "").strip()
                lang = data.get("language", session.language)
                if not user_text:
                    continue

                session.is_interrupted = False
                session.state = "processing"
                await websocket.send_json({
                    "type": "state_change",
                    "state": "processing"
                })
                await websocket.send_json({
                    "type": "user_transcript",
                    "text": user_text
                })

                # Process automotive reasoning
                response_text, vehicles = await voice_service.process_user_intent(user_text, language=lang)

                if session.is_interrupted:
                    continue

                session.state = "speaking"
                await websocket.send_json({
                    "type": "state_change",
                    "state": "speaking"
                })
                await websocket.send_json({
                    "type": "agent_transcript",
                    "text": response_text
                })

                if vehicles:
                    await websocket.send_json({
                        "type": "vehicle_cards",
                        "vehicles": vehicles
                    })

                # Stream synthesized audio chunks
                wav_bytes = voice_service.generate_speech_wav(response_text)
                audio_b64 = base64.b64encode(wav_bytes).decode("ascii")

                await websocket.send_json({
                    "type": "audio_chunk",
                    "data": audio_b64,
                    "sample_rate": 16000
                })

                session.state = "listening"
                await websocket.send_json({
                    "type": "state_change",
                    "state": "listening"
                })

            elif msg_type == "audio_chunk":
                # Received streaming audio from microphone
                session.state = "listening"
                # If end-of-speech or turn boundary triggered by client VAD
                if data.get("is_final", False):
                    client_transcript = data.get("transcript", "")
                    lang = data.get("language", session.language)
                    
                    if not client_transcript:
                        client_transcript = "Tell me about available SUVs" if lang == "en" else "നല്ലൊരു SUV വേണം"

                    session.state = "processing"
                    await websocket.send_json({
                        "type": "state_change",
                        "state": "processing"
                    })
                    await websocket.send_json({
                        "type": "user_transcript",
                        "text": client_transcript
                    })

                    response_text, vehicles = await voice_service.process_user_intent(client_transcript, language=lang)

                    session.state = "speaking"
                    await websocket.send_json({
                        "type": "state_change",
                        "state": "speaking"
                    })
                    await websocket.send_json({
                        "type": "agent_transcript",
                        "text": response_text
                    })

                    if vehicles:
                        await websocket.send_json({
                            "type": "vehicle_cards",
                            "vehicles": vehicles
                        })

                    wav_bytes = voice_service.generate_speech_wav(response_text)
                    audio_b64 = base64.b64encode(wav_bytes).decode("ascii")

                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": audio_b64
                    })

                    session.state = "listening"
                    await websocket.send_json({
                        "type": "state_change",
                        "state": "listening"
                    })

            elif msg_type == "stop":
                session.state = "ended"
                await websocket.send_json({
                    "type": "state_change",
                    "state": "ended"
                })
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {e}")
    finally:
        voice_service.close_session(session_id)
