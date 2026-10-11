from typing import Dict


def analyze_semantics(transcript: str) -> Dict[str, object]:
    text = transcript.lower()
    return {
        "semantic_tags": ["problem_reporting", "help_seeking"] if "not working" in text or "help" in text else ["general_conversation"],
        "criticality": "high" if "not working" in text or "problem" in text else "medium",
    }
