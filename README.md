# Human State Representation for Real-Time Emotion-Aware Context Generation

This project implements a modular, explainable, deterministic prototype for converting audio into a structured Human State Representation (HSR) without using an LLM.

## Scope implemented

- FastAPI backend with health and analysis endpoints
- Audio preprocessing pipeline scaffolding
- Speech/transcription and emotion/intent inference adapters
- HSRE evidence fusion + rule-based reasoning + probabilistic scoring
- Lightweight in-memory conversation memory
- React + Vite frontend for upload and analysis
- Dockerfiles and deployment config for Render and Vercel

## Architecture

- Backend: FastAPI
- Frontend: React + Vite
- Deployment:
  - Render for the FastAPI backend
  - Vercel for the frontend

## Important implementation note

The specification names real models such as Whisper Small, HuBERT Base, BGE-M3, and Silero VAD. This repository implements a working prototype using deterministic, explainable logic and pluggable model adapters so those models can be swapped in later without changing the interface.

The project does not use an LLM, and the final output remains a structured HSR JSON.

## Local development

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

## API

- GET /api/health
- POST /api/analyze
- POST /api/analyze/stream (newline-delimited progress events for the interactive UI)
- POST /api/upload
- POST /api/recording

Model and audio behavior is documented in [MODEL_FAQ.md](MODEL_FAQ.md).

## Deployment

- Backend deploy target: Render
- Frontend deploy target: Vercel

See `render.yaml` and `frontend/vercel.json`.

## Notes

This is intentionally a research prototype: the first-pass implementation emphasizes modularity, deterministic reasoning, and deployment readiness over full model weight optimization.
