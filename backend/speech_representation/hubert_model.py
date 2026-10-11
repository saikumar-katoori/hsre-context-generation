from typing import Any, Dict

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency fallback
    np = None

from config.model_config import HUBERT_MODEL


def _load_hubert_components() -> tuple[Any, Any, Any] | tuple[None, None, None]:
    from config.settings import settings

    if settings.lightweight_mode:
        return None, None, None
    try:
        import torch
        from transformers import AutoFeatureExtractor, AutoModel

        feature_extractor = AutoFeatureExtractor.from_pretrained(HUBERT_MODEL)
        model = AutoModel.from_pretrained(HUBERT_MODEL)
        model.eval()
        return model, feature_extractor, torch
    except Exception:
        return None, None, None


def extract_speech_embedding(audio_path: str) -> Dict[str, Any]:
    if np is None:
        return {"embedding_available": False, "embedding_shape": [0, 0], "source": audio_path, "fallback": True}

    model, feature_extractor, torch = _load_hubert_components()
    if model is None or feature_extractor is None or torch is None:
        return {"embedding_available": False, "embedding_shape": [0, 0], "source": audio_path, "fallback": True}

    try:
        import soundfile as sf

        audio, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        inputs = feature_extractor(audio, sampling_rate=sample_rate, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        hidden = outputs.last_hidden_state
        pooled = hidden.mean(dim=1)
        vector = pooled[0].cpu().numpy().astype(float)
        return {
            "embedding_available": True,
            "embedding_shape": [int(vector.shape[0]), 1],
            "source": audio_path,
            "fallback": False,
            "embedding_preview": vector[:10].tolist(),
        }
    except Exception:
        return {"embedding_available": False, "embedding_shape": [0, 0], "source": audio_path, "fallback": True}
