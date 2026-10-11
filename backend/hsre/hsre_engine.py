from typing import Any, Dict

from hsre.evidence_fusion.fusion import fuse_evidence
from hsre.reasoning.probabilistic_scoring import compute_scores
from hsre.reasoning.rules import apply_rules
from hsre.reasoning.state_inference import infer_states
from hsre.state_constructor.constructor import build_human_state


class HSREngine:
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        evidence = fuse_evidence(payload)
        supporting = apply_rules(evidence)
        scores = compute_scores(evidence)
        inferred = infer_states(evidence, scores)
        human_state = build_human_state(inferred)

        return {
            "affective_state": {
                "emotion": inferred["affective_state"],
                "frustration_score": scores["frustration_score"],
                "confidence": scores["confidence"],
            },
            "cognitive_state": {
                "intent": inferred["cognitive_state"],
                "confidence": scores["confidence"],
                "uncertainty": round(max(0.0, 1.0 - scores["confidence"]), 3),
            },
            "interaction_state": {
                "state": inferred["interaction_state"],
                "confidence": scores["confidence"],
            },
            "communication_need": {
                "primary": inferred["communication_need"],
                "secondary": "empathy" if inferred["communication_need"] == "clarification" else "clarification",
                "recommended_detail": "step_by_step" if inferred["communication_need"] in {"clarification", "detailed_response"} else "concise",
            },
            "reasoning": {
                "supporting_evidence": supporting,
            },
            "structural_output": human_state,
        }
