from typing import Any, Dict

from config.hsre_config import HSRE_WEIGHTS


def compute_scores(evidence: Dict[str, Any]) -> Dict[str, Any]:
    emotion_confidence = evidence.get("emotion_evidence", {}).get("confidence", 0.0)
    emotion_intensity = evidence.get("emotion_evidence", {}).get("intensity", 0.0)
    intent_confidence = evidence.get("intent_evidence", {}).get("confidence", 0.0)
    negative_tripwire = emotion_confidence * 0.85 + emotion_intensity * 0.65

    frustration_score = (
        emotion_confidence * HSRE_WEIGHTS["emotion_weight"]
        + intent_confidence * HSRE_WEIGHTS["intent_weight"]
        + min(negative_tripwire, 1.0) * HSRE_WEIGHTS["context_weight"]
        + emotion_intensity * HSRE_WEIGHTS["linguistic_weight"]
    )

    return {
        "frustration_score": round(max(0.0, min(1.0, frustration_score)), 3),
        "confidence": round(max(0.0, min(1.0, (emotion_confidence + intent_confidence) / 2.0)), 3),
    }
