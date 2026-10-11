from fastapi.testclient import TestClient

from emotion_detection.inference import infer_emotion
from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_infer_emotion_changes_by_transcript_content():
    neutral_result = infer_emotion("/tmp/neutral.wav", "I am having a normal conversation with a friend.")
    frustrated_result = infer_emotion("/tmp/angry.wav", "I am really frustrated and this is not working.")

    assert neutral_result["emotion"] != frustrated_result["emotion"]
    assert frustrated_result["emotion"] in {"angry", "frustrated"}
    assert neutral_result["emotion"] in {"neutral", "happy", "sad"}
