from typing import Any, Dict


def fuse_evidence(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript = payload.get("transcript", "")
    emotion = payload.get("emotion", {})
    intent = payload.get("intent", {})
    history = payload.get("conversation_history", [])

    return {
        "emotion_evidence": {
            "label": emotion.get("emotion", "neutral"),
            "confidence": emotion.get("confidence", 0.0),
            "intensity": emotion.get("intensity", 0.0),
            "probabilities": emotion.get("probabilities", {}),
        },
        "linguistic_evidence": {
            "transcript": transcript,
            "length": len(transcript.split()),
        },
        "intent_evidence": {
            "label": intent.get("intent", "unknown"),
            "confidence": intent.get("confidence", 0.0),
        },
        "contextual_evidence": {
            "conversation_history_count": len(history),
            "has_repeated_failure": any("not working" in str(item).lower() for item in history),
        },
    }
