from typing import Any, Dict

from config.model_config import EMOTION_MODEL
from speech_representation.hubert_model import extract_speech_embedding


_MODEL_CACHE: Dict[str, Any] = {}


def _load_speech_emotion_model() -> Dict[str, Any]:
    from config.settings import settings

    if settings.lightweight_mode:
        return {"feature_extractor": None, "model": None, "torch": None}

    if "emotion_model" in _MODEL_CACHE:
        return _MODEL_CACHE["emotion_model"]

    try:
        import torch
        from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

        feature_extractor = AutoFeatureExtractor.from_pretrained(EMOTION_MODEL)
        model = AutoModelForAudioClassification.from_pretrained(EMOTION_MODEL)
        model.eval()
        _MODEL_CACHE["emotion_model"] = {
            "feature_extractor": feature_extractor,
            "model": model,
            "torch": torch,
        }
        return _MODEL_CACHE["emotion_model"]
    except Exception:
        _MODEL_CACHE["emotion_model"] = {"feature_extractor": None, "model": None, "torch": None}
        return _MODEL_CACHE["emotion_model"]


def _extract_audio_features(audio_path: str) -> Dict[str, float]:
    try:
        import numpy as np
        import soundfile as sf

        audio, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        audio = np.asarray(audio, dtype=np.float32)
        rms = float(np.sqrt(np.mean(np.square(audio))))
        abs_mean = float(np.mean(np.abs(audio)))
        zcr = float(np.mean(np.abs(np.diff(np.sign(audio))))) if len(audio) > 1 else 0.0
        return {"rms": rms, "abs_mean": abs_mean, "zcr": zcr, "sample_rate": float(sample_rate)}
    except Exception:
        return {"rms": 0.0, "abs_mean": 0.0, "zcr": 0.0, "sample_rate": 0.0}


def _map_model_label(label: str) -> str:
    normalized = (label or "").lower().replace(" ", "_")
    aliases = {
        "neutral": "neutral",
        "happy": "happy",
        "sad": "sad",
        "angry": "angry",
        "fear": "fear",
        "fearful": "fear",
        "surprised": "surprise",
        "surprise": "surprise",
        "disgust": "disgust",
        "disgusted": "disgust",
        "frustrated": "frustrated",
        "frustration": "frustrated",
        "annoyed": "frustrated",
        "mad": "frustrated",
        "anger": "angry",
        "happiness": "happy",
        "sadness": "sad",
    }
    return aliases.get(normalized, normalized)


def _predict_with_model(audio_path: str) -> Dict[str, Any]:
    model_info = _load_speech_emotion_model()
    if model_info["model"] is None or model_info["feature_extractor"] is None:
        return {}

    try:
        import numpy as np
        import soundfile as sf

        audio, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        inputs = model_info["feature_extractor"](audio, sampling_rate=sample_rate, return_tensors="pt")
        with model_info["torch"].no_grad():
            logits = model_info["model"](**inputs).logits

        probabilities = model_info["torch"].softmax(logits, dim=-1)[0]
        scores = probabilities.cpu().numpy().tolist()
        labels = model_info["model"].config.id2label
        outputs = []
        for index, score in enumerate(scores):
            label = _map_model_label(str(labels.get(index, str(index))))
            outputs.append({"label": label, "score": float(score)})

        top_result = max(outputs, key=lambda item: item["score"])
        output = {
            "emotion": top_result["label"],
            "confidence": round(float(top_result["score"]), 3),
            "probabilities": {item["label"]: round(float(item["score"]), 4) for item in outputs},
        }
        if output["emotion"] not in {"neutral", "happy", "sad", "angry", "fear", "surprise", "disgust", "frustrated"}:
            output["emotion"] = "neutral"
        return output
    except Exception:
        return {}


def infer_emotion(audio_path: str, transcript: str) -> Dict[str, Any]:
    """Use a pretrained speech model when available and preserve deterministic fallback logic otherwise."""
    transcript_lower = (transcript or "").lower()
    embedding_info = extract_speech_embedding(audio_path)
    audio_features = _extract_audio_features(audio_path)

    model_prediction = _predict_with_model(audio_path)
    if model_prediction:
        emotion = model_prediction["emotion"]
        confidence = model_prediction["confidence"]
        probabilities = model_prediction["probabilities"]
    else:
        scores = {
            "neutral": 0.8,
            "happy": 0.0,
            "sad": 0.0,
            "angry": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "frustrated": 0.0,
        }

        cue_map = {
            "happy": ["happy", "great", "good", "excited", "love", "awesome", "excellent"],
            "sad": ["sad", "down", "disappointed", "upset", "crying", "depressed", "sorry"],
            "angry": ["angry", "annoyed", "mad", "rage", "furious", "hate this"],
            "fear": ["scared", "afraid", "nervous", "worried", "panic", "unsafe"],
            "surprise": ["surprised", "unexpected", "wow", "oh no", "what happened"],
            "disgust": ["disgusted", "gross", "awful", "nasty", "terrible"],
            "frustrated": ["frustrated", "not working", "still not working", "broken", "stuck", "can't continue"],
        }

        for label, phrases in cue_map.items():
            for phrase in phrases:
                if phrase in transcript_lower:
                    scores[label] += 2.5

        if "help" in transcript_lower or "need help" in transcript_lower:
            scores["frustrated"] += 1.5
            scores["neutral"] -= 0.3
        if "problem" in transcript_lower or "issue" in transcript_lower:
            scores["frustrated"] += 1.2
        if "thank you" in transcript_lower or "glad" in transcript_lower:
            scores["happy"] += 1.2

        if audio_features["rms"] > 0.18:
            scores["angry"] += 0.8
            scores["frustrated"] += 0.5
        if audio_features["rms"] < 0.08 and audio_features["abs_mean"] < 0.06:
            scores["sad"] += 0.7
            scores["neutral"] += 0.3
        if audio_features["zcr"] > 0.12:
            scores["surprise"] += 0.4
            scores["happy"] += 0.2

        if not transcript_lower.strip():
            scores["neutral"] = max(1.0, scores["neutral"])

        emotion = max(scores, key=scores.get)
        if emotion == "frustrated" and scores["frustrated"] < 1.0:
            emotion = "neutral"

        probabilities = {label: max(0.02, min(0.95, score / max(sum(scores.values()), 1.0))) for label, score in scores.items()}
        probability_total = sum(probabilities.values())
        probabilities = {label: round(value / probability_total, 4) for label, value in probabilities.items()}
        confidence = max(0.35, min(0.98, 0.4 + 0.25 * (scores[emotion] / max(sum(scores.values()), 1.0)) + (0.12 if embedding_info.get("embedding_available") else 0.0)))

    intensity = max(0.12, min(0.96, 0.2 + 0.4 * (confidence if confidence > 0.0 else 0.5)))
    if "frustrated" in str(probabilities).lower() and confidence < 0.5:
        intensity = max(intensity, 0.5)

    return {
        "emotion": emotion,
        "confidence": round(float(confidence), 3),
        "intensity": round(float(intensity), 3),
        "probabilities": probabilities,
        "speech_representation": embedding_info,
    }
