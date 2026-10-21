import json
import base64
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from app.schemas.health import APIEnvelope
from app.schemas.voice import (
    VoiceSessionCreate,
    VoiceSessionResponse,
    VoiceTextRequest,
    VoiceTextResponse,
    FeedbackCreate,
    ToolExecutionTrace
)
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
    Typed fallback endpoint that returns answer, vehicle recommendations, tool traces, and audio synthesis.
    """
    response_text, recommended_vehicles, tool_trace, memory = await voice_service.process_user_intent(
        text=payload.text,
        language=payload.language,
        session_id=payload.session_id
    )
    
    # Synthesize audio for the response
    wav_bytes = voice_service.generate_speech_wav(response_text)
    audio_b64 = base64.b64encode(wav_bytes).decode("ascii")

    tool_exec_obj = None
    if tool_trace:
        tool_exec_obj = ToolExecutionTrace(**tool_trace)

    res = VoiceTextResponse(
        session_id=payload.session_id,
        user_text=payload.text,
        response_text=response_text,
        audio_base64=audio_b64,
        language=payload.language,
        recommended_vehicles=recommended_vehicles,
        state="idle",
        tool_executed=tool_exec_obj,
        session_memory=memory
    )
    return APIEnvelope[VoiceTextResponse](data=res)


@router.post("/feedback", response_model=APIEnvelope[dict])
async def record_feedback(payload: FeedbackCreate):
    """
    Records customer evaluation feedback (thumbs up/down, reasons) for self-improving agent performance.
    """
    saved_record = voice_service.add_feedback(payload.model_dump())
    return APIEnvelope[dict](data=saved_record)


@router.get("/evaluation", response_model=APIEnvelope[dict])
async def get_agent_evaluation():
    """
    Returns real-time agent evaluation metrics, benchmark scores, CSAT, and guardrails.
    """
    metrics = voice_service.get_evaluation_metrics()
    return APIEnvelope[dict](data=metrics)


@router.post("/evaluate-benchmark", response_model=APIEnvelope[dict])
async def run_benchmark_evaluation():
    """
    Executes automated synthetic evaluation suite comparing intent accuracy, latency, and tool invocations.
    """
    results = voice_service.run_benchmark_suite()
    return APIEnvelope[dict](data=results)


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
            "language": session.language,
            "session_id": session.session_id
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

                # Process automotive reasoning with tool execution & memory
                response_text, vehicles, tool_trace, memory = await voice_service.process_user_intent(
                    user_text, language=lang, session_id=session.session_id
                )

                if session.is_interrupted:
                    continue

                if tool_trace:
                    await websocket.send_json({
                        "type": "tool_executed",
                        "tool": tool_trace
                    })

                if memory:
                    await websocket.send_json({
                        "type": "memory_updated",
                        "memory": memory
                    })

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
                session.state = "listening"
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

                    response_text, vehicles, tool_trace, memory = await voice_service.process_user_intent(
                        client_transcript, language=lang, session_id=session.session_id
                    )

                    if tool_trace:
                        await websocket.send_json({
                            "type": "tool_executed",
                            "tool": tool_trace
                        })

                    if memory:
                        await websocket.send_json({
                            "type": "memory_updated",
                            "memory": memory
                        })

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
