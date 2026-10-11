# HSRE Context Generation: Implementation Guide

## 1. Purpose

This project converts a short voice sample into a structured **Human State Representation (HSR)**. The output describes observable interaction state, such as likely affect, intent, frustration, uncertainty, and the kind of response that may be useful.

The project is deliberately **not** a conversational generative model. It does not generate an answer, imitate a person, diagnose a person, or make a clinical psychological judgment. It extracts evidence from audio and combines that evidence with deterministic reasoning.

The most important design constraint is:

> No LLM is used in the processing or reasoning path.

## 2. What is implemented versus planned

This repository is a working prototype with pluggable model adapters. The specification names Whisper Small, HuBERT Base, BGE-M3, Silero VAD, and a fine-tuned HuBERT emotion classifier. The checked-in implementation currently behaves as follows:

| Capability | Current implementation | Status |
|---|---|---|
| Audio normalization | `librosa` loads mono audio at 16 kHz and `soundfile` writes normalized WAV | Implemented |
| Size and duration limits | 25 MB maximum and 15 seconds maximum | Implemented |
| Speech-to-text | Whisper Small adapter, with a deterministic filename-based fallback when unavailable | Implemented with fallback |
| Speech representation | HuBERT Base adapter, mean-pooled into a vector | Implemented when dependencies/checkpoint are available |
| Emotion | Configured speech-emotion checkpoint, with transparent transcript/audio-feature fallback | Implemented with fallback |
| Intent | Deterministic keyword rules | Implemented |
| BGE-M3 semantics | Model identifier is configured, but BGE-M3 is not loaded by the current intent path | Planned adapter |
| VAD | Mentioned in the specification, but not currently called by preprocessing | Planned enhancement |
| HSR reasoning | Evidence fusion, rules, weighted score, state inference, and output construction | Implemented |
| Conversation memory | In-memory helper exists, but the current inference request passes an empty history | Scaffold |
| Streaming | Newline-delimited progress events for the UI | Implemented; this is progress streaming, not live token/audio streaming |

This distinction matters: a configured model name is not evidence that a model was trained or that it is active at runtime.

## 3. Repository structure

```text
hsre-context-generation/
|-- backend/
|   |-- main.py                         FastAPI application and CORS setup
|   |-- requirements.txt                Python runtime dependencies
|   |-- api/routes/
|   |   |-- health.py                    Health endpoint
|   |   |-- inference.py                 Analysis orchestration and NDJSON events
|   |   |-- upload.py                    Upload endpoint
|   |   `-- recording.py                 Recording-related endpoint
|   |-- audio_preprocessing/
|   |   `-- preprocessing.py             File limits, loading, mono/16 kHz normalization
|   |-- speech_to_text/
|   |   `-- transcriber.py               Whisper adapter and fallback transcript
|   |-- speech_representation/
|   |   `-- hubert_model.py               HuBERT feature extraction adapter
|   |-- emotion_detection/
|   |   `-- inference.py                 Emotion model adapter and fallback scoring
|   |-- language_analysis/
|   |   |-- intent_classifier.py          Explainable intent rules
|   |   `-- semantic_analysis.py          Lightweight semantic tags and criticality
|   |-- conversation_memory/
|   |   `-- memory.py                     In-memory recent interaction helper
|   |-- hsre/
|       |-- hsre_engine.py                HSRE orchestration boundary
|       |-- evidence_fusion/fusion.py     Common evidence schema
|       |-- reasoning/rules.py             Human-readable supporting evidence
|       |-- reasoning/probabilistic_scoring.py Weighted score calculation
|       |-- reasoning/state_inference.py   State mapping and response need
|       |-- state_constructor/constructor.py Stable output shape
|       `-- schemas/                       Reserved schema package
|   |-- config/
|       |-- model_config.py               Checkpoint identifiers and labels
|       |-- hsre_config.py                Weights and allowed state vocabularies
|       `-- settings.py                   Environment-backed service settings
|   `-- tests/test_api.py                 API tests
|-- frontend/
|   |-- src/App.jsx                       Recording, upload, progress, result display
|   |-- src/main.jsx                      React entry point
|   |-- src/styles.css                    Visual styling
|   |-- package.json                      React/Vite dependencies and scripts
|   `-- vite.config.js                    Vite configuration
|-- docker-compose.yml                    Local multi-service composition
|-- render.yaml                           Render backend deployment configuration
|-- HSR_Project_Implementation_Specification.md
|-- IMPLEMENTATION_GUIDE.md               This guide
`-- MODEL_FAQ.md                           Model and implementation FAQ
```

Each backend capability owns its adapter and public function. That keeps the HSR engine independent from a particular ASR, emotion, or embedding vendor.

## 4. End-to-end execution

### 4.1 Input and preprocessing

The frontend accepts an audio upload or records a browser clip. Browser recording is limited to 15 seconds and asks for 10-15 seconds. The backend stores the upload in `backend/tmp_audio/`, rejects empty files and files over 25 MB, then normalizes available audio libraries to:

- mono audio;
- 16 kHz sample rate;
- normalized amplitude;
- WAV output for downstream adapters.

The duration restriction is an application cost and latency control. It is not a Whisper limitation.

### 4.2 Extraction stage

`backend/api/routes/inference.py` owns the sequence:

1. Preprocess the file.
2. Call `transcribe_audio_detailed`.
3. Call `extract_speech_embedding`.
4. Call `infer_emotion`.
5. Call `infer_intent`.
6. Pass the structured evidence to `HSREngine.run`.
7. Return the final result and progress events.

The streaming endpoint emits newline-delimited JSON. This makes intermediate progress visible in the frontend without requiring a WebSocket or a full event broker.

### 4.3 Current model choices

#### Whisper Small

Whisper Small is used only for automatic speech recognition. It converts the waveform to text; it does not decide emotion or response strategy. It was chosen because it is a widely supported pretrained ASR checkpoint with multilingual capability and a substantially smaller runtime footprint than larger Whisper variants.

#### HuBERT Base

HuBERT Base is used as a speech representation model. The adapter mean-pools its last hidden state and returns a compact summary vector. The embedding is useful as a signal that a speech representation was extracted, but the current HSRE rules do not directly consume the vector.

HuBERT is a suitable choice for acoustic representation because it is designed to learn speech structure without requiring an LLM-style generation loop. Wav2Vec2, WavLM, or a task-specific acoustic classifier could replace it behind the same function.

#### Emotion checkpoint

The configured checkpoint is `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`. It is loaded through a generic Transformers audio-classification interface. Its labels are normalized into the project vocabulary where possible. The repository does not fine-tune this checkpoint and does not claim a measured accuracy for it.

If loading fails, the fallback combines transcript cues with simple waveform features: RMS energy, mean absolute amplitude, and zero-crossing rate. This makes the demo inspectable and runnable, but it is not equivalent to a trained emotion model.

#### BGE-M3

`BAAI/bge-m3` is configured as the semantic model named in the original specification. It is an embedding model, not a generative LLM. The current intent classifier does not load it; it uses deterministic phrase checks. BGE-M3 can be added later behind the same intent contract using similarity to labeled intent descriptions.

### 4.4 Intent and semantics

The current `infer_intent` function uses ordered phrase rules for help requests, feedback, disagreement, greetings, farewells, and information questions. It returns an intent label, confidence, and the allowed label vocabulary.

This was selected for the prototype because it is:

- easy to inspect and test;
- deterministic across machines;
- cheap on CPU;
- free of hidden prompt or generation behavior;
- replaceable without changing HSRE.

The tradeoff is limited language coverage. Keyword rules should not be presented as a general semantic understanding system.

## 5. Exact HSRE functionality

The HSR engine is the boundary between extracted evidence and the structured state output. `HSREngine.run` performs five operations:

```text
payload
  -> fuse_evidence
  -> apply_rules
  -> compute_scores
  -> infer_states
  -> build_human_state
```

### 5.1 Evidence fusion

`fuse_evidence` creates one stable structure from transcript, emotion, intent, and conversation history:

- emotion label, confidence, intensity, and probability map;
- transcript and word count;
- intent label and confidence;
- history count and a repeated-failure flag.

This prevents the reasoning layer from depending on model-specific response objects.

### 5.2 Supporting rules

`apply_rules` produces human-readable evidence strings. Examples include:

- negative emotion plus help-seeking intent;
- strong emotional confidence;
- repeated unsuccessful attempts in recent context;
- neutral or low-intensity interaction.

These strings are an explanation trace, not a generated explanation. They make it possible to inspect why the engine reached a state.

### 5.3 Weighted score

The current frustration score is bounded to $[0,1]$ and uses the configured weights:

$$
F = 0.45E_c + 0.25I_c + 0.20T + 0.10E_i
$$

where:

- $E_c$ is emotion confidence;
- $I_c$ is intent confidence;
- $T = \min(0.85E_c + 0.65E_i, 1)$ is the negative-emotion tripwire;
- $E_i$ is emotion intensity.

Overall confidence is the bounded average of emotion and intent confidence:

$$
C = \frac{E_c + I_c}{2}
$$

These are engineered scores, not calibrated probabilities. Calibration against a labeled, speaker-independent dataset is required before treating them as probabilistic claims.

### 5.4 State inference

The current mappings are intentionally small:

- `frustrated` or `angry` emotion -> affective state `frustrated`;
- `sad` -> `sad`;
- `happy` -> `happy`;
- help or information intent -> cognitive state `information_seeking`;
- disagreement -> `confused`;
- repeated failure or frustration score above `0.7` -> interaction state `repeated_failure`;
- help request -> `help_seeking` when repeated failure is not selected;
- frustrated affect -> communication need `empathy`;
- information seeking -> `detailed_response`.

The constructor then returns the stable HSR shape with affective, cognitive, interaction, communication, and reasoning sections.

## 6. Why this architecture was selected

### Why modular adapters?

Audio models change frequently and have different memory requirements. Keeping ASR, acoustic representation, emotion, intent, and HSRE behind small functions lets one component be replaced without rewriting the reasoning engine or frontend contract.

### Why deterministic HSRE instead of an LLM?

The task needs a bounded state object and an inspectable decision path, not free-form language generation. Rules and weighted scoring provide:

- repeatability;
- low inference cost;
- predictable output schema;
- visible evidence;
- straightforward unit testing;
- no prompt injection surface in the reasoning layer;
- easier review of sensitive emotion-related behavior.

An LLM could produce richer prose, but it would introduce generation latency, token cost, nondeterminism, harder calibration, and a less auditable path from evidence to state. It would also violate the project constraint.

### Why short clips instead of continuous voice streaming?

The prototype targets a bounded interaction sample. Fifteen seconds limits upload size, model work, memory, and worst-case latency while keeping the implementation deployable on modest infrastructure. The NDJSON endpoint gives the user progress feedback without claiming that the acoustic pipeline is operating continuously in real time.

### Why not use a single end-to-end real-time voice model?

An end-to-end voice model combines several expensive and difficult concerns: streaming audio buffering, ASR, acoustic understanding, emotion inference, turn detection, context management, and sometimes response generation. In practice this can fail or degrade because of:

- GPU memory pressure from several large models;
- compute spikes when audio chunks overlap;
- queueing and cold-start latency;
- network round trips when inference is hosted remotely;
- model loading time and bandwidth;
- difficult failure isolation when one combined component fails;
- unclear explanations and calibration;
- higher per-minute or per-token service cost.

These are engineering tradeoffs, not a claim that all real-time voice models fail. A well-operated streaming system can work, but it normally needs more infrastructure and careful optimization than this prototype.

### Why this can be the cheaper alternative

The cost advantage comes from the architecture, not from a guarantee of free inference:

1. A short input bounds work per request.
2. The HSRE stage uses ordinary Python arithmetic and string matching.
3. Model adapters are optional and can run locally on CPU for small workloads.
4. Progress streaming avoids a separate realtime transport stack.
5. Components can be scaled or replaced independently.
6. The system does not pay for generated response tokens.

If hosted model inference is used, Whisper, emotion, and HuBERT still have compute and egress costs. The correct way to demonstrate savings is to benchmark identical clips and report latency, CPU/GPU time, memory, failure rate, and cost per analyzed minute.

## 7. What makes the project distinctive

The distinctive property is the separation between **evidence extraction** and **human-state reasoning**. Many voice systems jump from audio to a response. This project exposes an intermediate, structured, reviewable state:

```json
{
  "affective_state": {"emotion": "frustrated", "frustration_score": 0.81, "confidence": 0.79},
  "cognitive_state": {"intent": "information_seeking", "confidence": 0.79, "uncertainty": 0.21},
  "interaction_state": {"state": "help_seeking", "confidence": 0.79},
  "communication_need": {"primary": "empathy", "secondary": "clarification", "recommended_detail": "concise"},
  "reasoning": {"supporting_evidence": ["strong emotional confidence"]}
}
```

Compared with an end-to-end generative voice assistant, this approach is more transparent and easier to test. Compared with a simple sentiment classifier, it combines affect, intent, interaction history, confidence, uncertainty, and communication guidance. Compared with a large always-on streaming stack, it has a smaller operational footprint and a bounded request cost.

The tradeoff is equally important: it currently has narrower language coverage, limited history wiring, no calibrated benchmark, and fallback heuristics that should not be mistaken for production-grade emotion recognition.

## 8. API and frontend contract

The backend exposes:

- `GET /api/health` for service health;
- `POST /api/analyze` for one complete JSON response;
- `POST /api/analyze/stream` for newline-delimited progress events;
- `POST /api/upload` for upload handling;
- `POST /api/recording` for recording-related integration.

The React frontend uses `VITE_API_URL`, records through `MediaRecorder`, submits `multipart/form-data`, reads the NDJSON stream, shows pipeline stages, and renders the transcript, emotion, intent, and final HSR JSON.

## 9. Limitations and responsible interpretation

- Emotion labels are estimates from speech signals and must not be treated as diagnoses.
- Confidence values are not calibrated probabilities.
- English is the reliable end-to-end target because intent rules and the configured emotion checkpoint are English-oriented.
- The current implementation is short-clip analysis with progress streaming, not low-latency continuous voice interaction.
- The fallback transcript may derive text from the filename; this is a demo fallback and should be disabled in a production system.
- Temporary audio files require an explicit retention and deletion policy in production.
- A real evaluation needs a speaker-independent dataset, fixed labels, model versions, latency measurements, and failure reporting.

## 10. Recommended production next steps

1. Add explicit schemas with Pydantic for extraction evidence and HSR output.
2. Add tests for every intent, emotion mapping, score boundary, and history condition.
3. Replace filename-based fallback behavior with an explicit unavailable state.
4. Add real VAD and cleanup of temporary audio.
5. Wire conversation memory into the request lifecycle with bounded retention.
6. Add optional BGE-M3 similarity intent classification and compare it against rules.
7. Calibrate confidence and evaluate on speaker-independent data.
8. Benchmark CPU, GPU, memory, latency, and cost against a continuous voice baseline.
