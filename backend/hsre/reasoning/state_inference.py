from typing import Any, Dict


def infer_states(evidence: Dict[str, Any], score: Dict[str, Any]) -> Dict[str, Any]:
    emotion_label = evidence.get("emotion_evidence", {}).get("label", "neutral")
    intent_label = evidence.get("intent_evidence", {}).get("label", "unknown")
    repeated_failure = evidence.get("contextual_evidence", {}).get("has_repeated_failure", False)

    affective = "neutral"
    if emotion_label in {"frustrated", "angry"}:
        affective = "frustrated"
    elif emotion_label == "sad":
        affective = "sad"
    elif emotion_label == "happy":
        affective = "happy"

    cognitive = "information_seeking"
    if intent_label in {"requesting_help", "asking_information"}:
        cognitive = "information_seeking"
    elif intent_label == "disagreement":
        cognitive = "confused"

    interaction = "normal_interaction"
    if repeated_failure or score["frustration_score"] > 0.7:
        interaction = "repeated_failure"
    elif intent_label == "requesting_help":
        interaction = "help_seeking"

    communication_need = "clarification"
    if affective == "frustrated":
        communication_need = "empathy"
    elif cognitive == "information_seeking":
        communication_need = "detailed_response"

    return {
        "affective_state": affective,
        "cognitive_state": cognitive,
        "interaction_state": interaction,
        "communication_need": communication_need,
        "score": score,
    }
