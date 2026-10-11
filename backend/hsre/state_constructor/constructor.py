from typing import Any, Dict


def build_human_state(output: Dict[str, Any]) -> Dict[str, Any]:
    affective = output.get("affective_state", "neutral")
    cognitive = output.get("cognitive_state", "information_seeking")
    interaction = output.get("interaction_state", "normal_interaction")
    communication = output.get("communication_need", "clarification")
    score = output.get("score", {})

    return {
        "affective_state": {
            "emotion": affective,
            "frustration_score": score.get("frustration_score", 0.0),
            "confidence": score.get("confidence", 0.0),
        },
        "cognitive_state": {
            "intent": cognitive,
            "confidence": score.get("confidence", 0.0),
            "uncertainty": round(max(0.0, 1.0 - score.get("confidence", 0.0)), 3),
        },
        "interaction_state": {
            "state": interaction,
            "confidence": score.get("confidence", 0.0),
        },
        "communication_need": {
            "primary": communication,
            "secondary": "empathy" if communication == "clarification" else "clarification",
            "recommended_detail": "step_by_step" if communication in {"clarification", "detailed_response"} else "concise",
        },
    }
