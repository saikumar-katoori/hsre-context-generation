HSRE_WEIGHTS = {
    "emotion_weight": 0.45,
    "intent_weight": 0.25,
    "context_weight": 0.20,
    "linguistic_weight": 0.10,
    "negative_emotion_threshold": 0.75,
    "confidence_floor": 0.10,
}

INTENT_LABELS = [
    "asking_information",
    "requesting_help",
    "complaint",
    "confirmation",
    "disagreement",
    "feedback",
    "greeting",
    "farewell",
    "troubleshooting",
    "unknown",
]

AFFECTIVE_STATES = ["calm", "happy", "sad", "angry", "fearful", "frustrated", "excited", "neutral"]
COGNITIVE_STATES = ["confused", "focused", "uncertain", "confident", "information_seeking"]
INTERACTION_STATES = ["casual", "help_seeking", "repeated_failure", "disagreement", "escalation", "normal_interaction"]
COMMUNICATION_NEEDS = ["reassurance", "clarification", "concise_response", "detailed_response", "empathy", "encouragement", "direct_answer"]
