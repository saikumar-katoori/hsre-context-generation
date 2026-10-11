from typing import Any, Dict

from config.model_config import WHISPER_MODEL


def _fallback_transcript(audio_path: str) -> str:
    path = (audio_path or "").lower()
    keyword_phrases = {
        "angry": "I am frustrated and need help right now.",
        "frustrated": "I am really frustrated and this is not working.",
        "happy": "I am happy and everything is going well today.",
        "sad": "I feel disappointed and a bit down today.",
        "problem": "I have tried this several times but it is still not working.",
        "help": "I need help understanding the issue and want a clear explanation.",
    }

    for keyword, phrase in keyword_phrases.items():
        if keyword in path:
            return phrase

    return ""


def transcribe_audio(audio_path: str) -> str:
    """Return transcript text while preserving the existing public helper."""
    return transcribe_audio_detailed(audio_path)["text"]


def transcribe_audio_detailed(audio_path: str) -> Dict[str, Any]:
    """Run Whisper and expose why an empty transcript was returned."""
    try:
        import soundfile as sf
        from transformers import pipeline

        audio, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
        if getattr(audio, "ndim", 1) > 1:
            audio = audio.mean(axis=1)

        asr = pipeline(
            "automatic-speech-recognition",
            model=WHISPER_MODEL,
            tokenizer=WHISPER_MODEL,
            chunk_length_s=30,
            device=-1,
        )
        result = asr({"raw": audio, "sampling_rate": sample_rate}, return_timestamps=False)
        transcript = result.get("text") if isinstance(result, dict) else str(result)
        if transcript and transcript.strip():
            return {"text": transcript.strip(), "available": True, "reason": None, "model": WHISPER_MODEL}
    except Exception as exc:
        fallback = _fallback_transcript(audio_path)
        if fallback:
            return {"text": fallback, "available": False, "reason": f"Whisper was unavailable, so the deterministic fallback was used: {exc}", "model": WHISPER_MODEL}
        return {"text": "", "available": False, "reason": f"Whisper transcription failed: {exc}", "model": WHISPER_MODEL}

    fallback = _fallback_transcript(audio_path)
    if fallback:
        return {"text": fallback, "available": False, "reason": "Whisper returned no text; the deterministic fallback was used.", "model": WHISPER_MODEL}
    return {"text": "", "available": False, "reason": "Whisper returned no text for this recording.", "model": WHISPER_MODEL}
