import os
import uuid
from pathlib import Path
from typing import Any, Dict
from fastapi import HTTPException, UploadFile

MAX_AUDIO_BYTES = 25 * 1024 * 1024
MAX_AUDIO_SECONDS = 15.0

try:
    import librosa
    import soundfile as sf
except Exception:  # pragma: no cover - optional runtime dependency fallback
    librosa = None
    sf = None


def normalize_audio(path: str) -> Dict[str, Any]:
    if librosa is None or sf is None:
        return {"path": path, "sample_rate": 16000, "duration": 0.0}

    waveform, sample_rate = librosa.load(path, sr=16000, mono=True)
    waveform = librosa.util.normalize(waveform)
    output_path = str(Path(path).with_name(f"normalized_{uuid.uuid4().hex}.wav"))
    sf.write(output_path, waveform, sample_rate)
    return {"path": output_path, "sample_rate": sample_rate, "duration": float(len(waveform) / sample_rate)}


async def preprocess_audio(file: UploadFile) -> str:
    upload_dir = Path("./tmp_audio")
    upload_dir.mkdir(exist_ok=True)

    audio_path = upload_dir / f"{uuid.uuid4().hex}_{file.filename or 'audio.wav'}"
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded audio file is empty.")
    if len(contents) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio files must be 25 MB or smaller.")
    audio_path.write_bytes(contents)

    normalized = normalize_audio(str(audio_path))
    if normalized["duration"] > MAX_AUDIO_SECONDS:
        raise HTTPException(status_code=413, detail="Audio recordings must be 15 seconds or shorter.")
    return normalized["path"]
