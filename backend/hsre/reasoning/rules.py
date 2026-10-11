from typing import Dict, List


def apply_rules(evidence: Dict[str, Any]) -> List[str]:
    supporting: List[str] = []

    emotion_label = evidence.get("emotion_evidence", {}).get("label", "neutral")
    intent_label = evidence.get("intent_evidence", {}).get("label", "unknown")
    emotion_confidence = evidence.get("emotion_evidence", {}).get("confidence", 0.0)
    repeated_failure = evidence.get("contextual_evidence", {}).get("has_repeated_failure", False)

    if emotion_label in {"angry", "frustrated"} and intent_label == "requesting_help":
        supporting.append("high negative emotional intensity with help-seeking intent")
    if emotion_confidence > 0.75:
        supporting.append("strong emotional confidence")
    if repeated_failure:
        supporting.append("repeated unsuccessful attempts in recent context")
    if not supporting:
        supporting.append("neutral or low-intensity interaction")

    return supporting
