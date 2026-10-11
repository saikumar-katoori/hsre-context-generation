import json
from typing import Any, AsyncIterator, Dict, Iterator

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from audio_preprocessing.preprocessing import preprocess_audio
from emotion_detection.inference import infer_emotion
from hsre.hsre_engine import HSREngine
from language_analysis.intent_classifier import infer_intent
from speech_representation.hubert_model import extract_speech_embedding
from speech_to_text.transcriber import transcribe_audio_detailed

router = APIRouter(prefix="/api", tags=["inference"])
engine = HSREngine()


def _event(stage: str, status: str, message: str, data: Any = None) -> Dict[str, Any]:
    event = {"stage": stage, "status": status, "message": message}
    if data is not None:
        event["data"] = data
    return event


def _run_analysis(audio_path: str) -> Iterator[Dict[str, Any]]:
    yield _event("preprocessing", "complete", "Audio normalized and validated.")
    transcription = transcribe_audio_detailed(audio_path)
    transcript = transcription["text"]
    yield _event("transcription", "complete" if transcript else "warning", "Transcript generated." if transcript else transcription["reason"], {
        "text": transcript, "available": transcription["available"], "reason": transcription["reason"],
    })

    speech_embedding = extract_speech_embedding(audio_path)
    yield _event("speech_representation", "complete", "Speech representation extracted.", speech_embedding)
    emotion = infer_emotion(audio_path, transcript)
    yield _event("emotion", "complete", "Emotion analyzed.", {
        "emotion": emotion["emotion"], "confidence": emotion["confidence"], "intensity": emotion["intensity"],
    })
    intent = infer_intent(transcript)
    yield _event("intent", "complete" if transcript else "warning", "Intent inferred." if transcript else "Intent could not be inferred because the transcript is empty.", {
        "intent": intent["intent"], "confidence": intent["confidence"], "reason": None if transcript else "No transcript text was available.",
    })

    hsr = engine.run({"transcript": transcript, "emotion": emotion, "intent": intent, "conversation_history": []})
    yield _event("hsr", "complete", "Human state representation assembled.", hsr)
    yield _event("complete", "complete", "Analysis complete.", {
        "status": "success", "input": {"source": "upload", "duration": 0.0}, "transcript": transcript,
        "transcript_status": transcription, "speech_representation": speech_embedding,
        "emotion_analysis": {"emotion": emotion["emotion"], "confidence": emotion["confidence"], "intensity": emotion["intensity"]},
        "intent_analysis": {"intent": intent["intent"], "confidence": intent["confidence"], "reason": None if transcript else "No transcript text was available."},
        "human_state": hsr,
    })


async def _analysis_events(file: UploadFile) -> AsyncIterator[Dict[str, Any]]:
    try:
        if not file.filename:
            raise ValueError("Audio file is required")
        audio_path = await preprocess_audio(file)
        for event in _run_analysis(audio_path):
            yield event
    except Exception as exc:
        yield _event("error", "error", str(exc))


@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)) -> dict:
    events = [event async for event in _analysis_events(file)]
    error_event = next((event for event in events if event["stage"] == "error"), None)
    if error_event:
        raise HTTPException(status_code=400, detail=error_event["message"])
    return next(event["data"] for event in events if event["stage"] == "complete")


@router.post("/analyze/stream")
async def analyze_audio_stream(file: UploadFile = File(...)) -> StreamingResponse:
    async def stream():
        async for event in _analysis_events(file):
            yield json.dumps(event) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")
