from typing import Any, Dict

from config.hsre_config import INTENT_LABELS


def infer_intent(transcript: str) -> Dict[str, Any]:
    text = transcript.lower()

    if "need help" in text or "not working" in text or "still not working" in text:
        return {"intent": "requesting_help", "confidence": 0.87, "intent_labels": INTENT_LABELS}
    if "thank" in text or "thanks" in text:
        return {"intent": "feedback", "confidence": 0.72, "intent_labels": INTENT_LABELS}
    if "no" in text or "disagree" in text:
        return {"intent": "disagreement", "confidence": 0.68, "intent_labels": INTENT_LABELS}
    if "hello" in text or "hi" in text:
        return {"intent": "greeting", "confidence": 0.81, "intent_labels": INTENT_LABELS}
    if "goodbye" in text or "bye" in text:
        return {"intent": "farewell", "confidence": 0.79, "intent_labels": INTENT_LABELS}
    if "why" in text or "how" in text:
        return {"intent": "asking_information", "confidence": 0.76, "intent_labels": INTENT_LABELS}
    return {"intent": "unknown", "confidence": 0.41, "intent_labels": INTENT_LABELS}
