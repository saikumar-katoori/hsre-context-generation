# Project Implementation Specification

## Project Title
**Human State Representation for Real-Time Emotion-Aware Context Generation**

---

## Project Objective

Build a real-time voice processing system that accepts either:

1. Recorded voice from the user's microphone
2. Uploaded audio file

The system must process the audio and produce a structured **Human State Representation (HSR)**.

The project has **two major phases**:

- **Phase 1** — Audio Processing + Speech/Text/Emotion Extraction
- **Phase 2** — Human State Representation Engine (HSRE)

### Important Constraints

- **DO NOT USE ANY LLM.**
- DO NOT use GPT, Gemini, Claude, Llama, Mistral, or any generative LLM.
- HSRE must be implemented using deterministic rules, NLP models, probability/state scoring, and structured logic.
- Keep every major module in its own folder.
- HSRE must have its own completely separate folder/module.
- Keep the implementation simple, modular, explainable, and fast.
- Do not introduce unnecessary technologies or features outside these requirements.

---

## High-Level Architecture

```
User
  |
  |-- Record Audio
  |-- Upload Audio
  |
  v
Audio Preprocessing Unit
  |
  v
Data Extraction Pipeline
  |
  |----------------------|
  |                      |
  v                      v
Speech-to-Text       Speech Representation
Whisper Small        HuBERT Base
  |                      |
  v                      v
Transcript           Speech Embeddings
                         |
                         v
                  Emotion Detection
                  Fine-tuned HuBERT
                         |
                         v
              Emotion + Confidence
                         |
                         v
              Language & Intent Analysis
                    BGE-M3
                         |
                         v
             Intent / Semantic Information
                         |
                         v
              Conversation Memory
                         |
                         v
        =================================
        PHASE 2: HSRE
        Human State Representation Engine
        =================================
                         |
                         v
                Evidence Fusion
                         |
                         v
             Rule-Based Reasoning
                         +
             Probabilistic State Scoring
                         |
                         v
                State Inference
                         |
                         v
             Human State Constructor
                         |
                         v
                Structured HSR JSON
                         |
                         v
              Return Result to Frontend
```

---

## Phase 1: Audio Processing and Information Extraction

Phase 1 is responsible **only** for converting raw audio into useful structured evidence. It must **not** perform Human State reasoning.

Phase 1 produces:

- Processed audio
- Transcript
- Speech embeddings
- Emotion probabilities
- Emotion confidence
- Emotion intensity
- Intent
- Semantic information

### Module 1: Audio Preprocessing

**Folder:** `backend/audio_preprocessing/`

**Purpose:** Convert raw microphone/uploaded audio into a standardized format.

**Input:**
- WAV
- MP3
- M4A
- Other common audio formats

**Processing:**
1. Load audio
2. Convert to mono
3. Resample to 16 kHz
4. Normalize amplitude
5. Voice Activity Detection
6. Remove unnecessary silence
7. Noise/filter processing if required
8. Frame/window the audio if required

**Models/tools:**
- Silero VAD
- Librosa
- torchaudio

**Output:** `processed_audio.wav`

**Example metadata:**
```json
{
    "sample_rate": 16000,
    "channels": 1,
    "duration": 4.82,
    "speech_duration": 3.91
}
```

---

### Module 2: Speech Representation

**Folder:** `backend/speech_representation/`

**Model:** HuBERT Base

**Purpose:** Extract contextual speech representations from processed audio.

**Input:** `processed_audio.wav`

**Output:** Speech embeddings

```json
{
    "embedding_shape": [T, 768]
}
```

Do **not** expose model internals to the frontend. The module should provide a clean function/API such as:

```python
extract_speech_embedding(audio)
```

The exact implementation should remain inside this module.

---

### Module 3: Speech-to-Text

**Folder:** `backend/speech_to_text/`

**Model:** Whisper Small

**Purpose:** Convert speech into text.

**Input:** Processed audio

**Output:** Transcript

```json
{
    "transcript": "I have tried this several times but it is still not working."
}
```

Whisper is used **only** for ASR. Do not use an LLM for transcription.

---

### Module 4: Emotion Detection

**Folder:** `backend/emotion_detection/`

**Model:** Fine-tuned HuBERT Base + lightweight classification head

**Purpose:** Detect emotional characteristics from speech.

**Input:** Processed audio / HuBERT representation

**Output:**
1. Predicted emotion
2. Emotion probability distribution
3. Confidence
4. Emotion intensity

```json
{
    "emotion": "frustrated",
    "confidence": 0.91,
    "intensity": 0.84,
    "probabilities": {
        "neutral": 0.04,
        "happy": 0.02,
        "sad": 0.08,
        "angry": 0.25,
        "frustrated": 0.61
    }
}
```

> **Important:** Do not simply return a single emotion label. Preserve the probability distribution because HSRE will use the probabilities as evidence. If the trained emotion model does not contain "frustrated" as a class, use the actual trained emotion classes and let HSRE derive higher-level states such as frustration from emotion + transcript + context.

---

### Module 5: Language and Intent Analysis

**Folder:** `backend/language_analysis/`

**Model:** BGE-M3

**Purpose:** Extract semantic information from the transcript.

BGE-M3 is an embedding model, **not** an LLM. Use it for:

- Semantic representation
- Intent similarity
- Context similarity
- Semantic matching

Do **not** use BGE-M3 as a generative model.

For intent detection, initially use an explainable intent classification approach based on embeddings and predefined intent descriptions.

**Example intents:**
- `asking_information`
- `requesting_help`
- `complaint`
- `confirmation`
- `disagreement`
- `feedback`
- `greeting`
- `farewell`
- `troubleshooting`
- `unknown`

**Example output:**
```json
{
    "intent": "requesting_help",
    "intent_confidence": 0.87,
    "semantic_embedding_available": true
}
```

---

## Phase 1 Output

After Phase 1, create one standardized evidence object.

```json
{
    "audio": {
        "sample_rate": 16000,
        "duration": 4.82
    },

    "transcript": "I have tried this several times but it is still not working.",

    "emotion": {
        "label": "angry",
        "confidence": 0.91,
        "intensity": 0.84,
        "probabilities": {
            "neutral": 0.04,
            "happy": 0.02,
            "sad": 0.08,
            "angry": 0.61,
            "fear": 0.05,
            "surprise": 0.02,
            "disgust": 0.18
        }
    },

    "intent": {
        "label": "requesting_help",
        "confidence": 0.87
    },

    "speech_representation": {
        "embedding_available": true
    }
}
```

This object becomes the **input to Phase 2**.

---

## Module 6: Conversation Memory

**Folder:** `backend/conversation_memory/`

**Purpose:** Maintain previous conversational information. Store only information necessary for the current conversation.

**Possible information:**
- Previous transcripts
- Previous emotions
- Previous intents
- Previous HSR states
- Previous interaction results
- Conversation summary if implemented without an LLM

Initially keep this simple. Use a lightweight in-memory/session-based implementation. Do **not** introduce a vector database unless it becomes necessary. The goal is a working research prototype, not unnecessary infrastructure.

---

## Phase 2: Human State Representation Engine (HSRE)

**Folder:** `backend/hsre/`

**This is the most important module.** HSRE is the primary proposed contribution of the project. It must be completely independent from the emotion model, ASR model, and frontend.

HSRE receives structured evidence and converts it into a Human State Representation. **HSRE must not use an LLM.**

### HSRE Internal Structure

```
backend/hsre/

    __init__.py

    evidence_fusion/
        __init__.py
        fusion.py
        normalization.py

    reasoning/
        __init__.py
        rules.py
        probabilistic_scoring.py
        state_inference.py

    state_constructor/
        __init__.py
        affective_state.py
        cognitive_state.py
        interaction_state.py
        communication_need.py
        constructor.py

    schemas/
        __init__.py
        hsr_schema.py
        evidence_schema.py

    hsre_engine.py
```

### 6.1 Evidence Fusion

**Folder:** `backend/hsre/evidence_fusion/`

**Inputs:**
- Emotion probabilities
- Emotion confidence
- Emotion intensity
- Transcript
- Intent
- Intent confidence
- Conversation history
- Semantic information

**Tasks:**
1. Normalize evidence
2. Align evidence
3. Assign confidence/weights
4. Prepare unified evidence object

```json
{
    "emotion_evidence": {},
    "linguistic_evidence": {},
    "intent_evidence": {},
    "contextual_evidence": {}
}
```

### 6.2 Reasoning Layer

**Folder:** `backend/hsre/reasoning/`

This layer performs the actual Human State inference, using **two** mechanisms:

**A. Rule-Based Reasoning**

Rules must be explicit and explainable.

```
IF:
    emotion = angry
    AND intent = requesting_help
THEN:
    communication_need = clarification
```

```
IF:
    negative emotion confidence > 0.75
    AND previous interaction contains repeated failure
THEN:
    interaction_state = frustrated_interaction
```

```
IF:
    emotion confidence < threshold
THEN:
    reduce influence of emotion evidence
```

**B. Probabilistic State Scoring**

Do not treat a prediction as absolute. Calculate state scores using weighted evidence.

```
frustration_score =
    emotion_score * emotion_weight
    + intent_score * intent_weight
    + contextual_score * context_weight
```

The exact weights must be configurable. Example configuration:

| Weight | Value |
|---|---|
| `emotion_weight` | 0.45 |
| `intent_weight` | 0.25 |
| `context_weight` | 0.20 |
| `linguistic_weight` | 0.10 |

These values should **not** be hardcoded throughout the code — keep them in one configuration file.

The output should contain:
- Inferred state
- Score
- Confidence
- Supporting evidence

### 6.3 State Inference

**Possible inferred states:**

**Affective State:**
`calm` · `happy` · `sad` · `angry` · `fearful` · `frustrated` · `excited` · `neutral`

**Cognitive State:**
`confused` · `focused` · `uncertain` · `confident` · `information_seeking`

**Interaction State:**
`casual` · `help_seeking` · `repeated_failure` · `disagreement` · `escalation` · `normal_interaction`

**Communication Need:**
`reassurance` · `clarification` · `concise_response` · `detailed_response` · `empathy` · `encouragement` · `direct_answer`

> **Important:** These are not medical diagnoses. The system must **never** claim that it has diagnosed depression, anxiety disorder, PTSD, mental illness, clinical stress disorder, or any psychiatric condition. The system only estimates conversational/affective states from available signals.

### 6.4 Human State Constructor

**Folder:** `backend/hsre/state_constructor/`

Combine inferred states into a standardized HSR object.

```json
{
    "affective_state": {
        "emotion": "angry",
        "confidence": 0.91,
        "intensity": 0.84,
        "frustration_score": 0.82
    },

    "cognitive_state": {
        "intent": "requesting_help",
        "confidence": 0.87,
        "uncertainty": 0.32
    },

    "interaction_state": {
        "state": "repeated_failure",
        "confidence": 0.79
    },

    "communication_need": {
        "primary": "clarification",
        "secondary": "empathy",
        "recommended_detail": "step_by_step"
    },

    "reasoning": {
        "supporting_evidence": [
            "high negative emotional intensity",
            "help-seeking intent",
            "repeated unsuccessful attempts"
        ]
    }
}
```

---

## Important: No LLM Prompt Generation

Do **not** create:
- Prompt generator using an LLM
- GPT reasoning
- Gemini reasoning
- Claude reasoning
- Llama reasoning
- Generative AI inside HSRE

The current project ends with a **Structured Human State Representation**. The HSR itself is the output of the research system.

If a future LLM integration is required, the HSR JSON can be passed to an external LLM later — but this implementation must **not** include an LLM.

---

## Final API Output

The backend should return a clean structured response.

```json
{
    "status": "success",

    "input": {
        "source": "microphone",
        "duration": 5.2
    },

    "transcript": "I have tried this several times but it is still not working.",

    "emotion_analysis": {
        "emotion": "angry",
        "confidence": 0.91,
        "intensity": 0.84
    },

    "intent_analysis": {
        "intent": "requesting_help",
        "confidence": 0.87
    },

    "human_state": {
        "affective_state": {
            "emotion": "angry",
            "frustration_score": 0.82
        },

        "cognitive_state": {
            "intent": "requesting_help"
        },

        "interaction_state": {
            "state": "repeated_failure"
        },

        "communication_need": {
            "primary": "clarification",
            "secondary": "empathy",
            "recommended_detail": "step_by_step"
        }
    }
}
```

---

## Application Architecture

Use a simple two-part application:

- **Frontend / Web Application:** Express.js
- **Backend / ML Inference API:** FastAPI

```
Browser
   |
   | Record / Upload Audio
   v
Express.js
   |
   | HTTP request
   v
FastAPI
   |
   v
Audio Preprocessing
   |
   v
Phase 1
   |
   v
Phase 2 - HSRE
   |
   v
Structured JSON
   |
   v
FastAPI
   |
   v
Express.js
   |
   v
Frontend Result
```

---

## Folder Structure

Use a clean monorepo structure.

```
project-root/

    README.md

    frontend/
        package.json
        src/
            components/
            pages/
            services/
            styles/
        public/

    backend/
        requirements.txt
        main.py

        api/
            __init__.py
            routes/
                health.py
                inference.py
                upload.py
                recording.py

        config/
            settings.py
            model_config.py
            hsre_config.py

        audio_preprocessing/
            __init__.py
            preprocessing.py
            vad.py
            normalization.py
            resampling.py

        speech_representation/
            __init__.py
            hubert_model.py
            feature_extractor.py

        speech_to_text/
            __init__.py
            whisper_model.py
            transcriber.py

        emotion_detection/
            __init__.py
            model.py
            classifier.py
            inference.py
            schemas.py

        language_analysis/
            __init__.py
            embedding_model.py
            intent_classifier.py
            semantic_analysis.py
            schemas.py

        conversation_memory/
            __init__.py
            memory.py
            session.py
            schemas.py

        hsre/
            __init__.py

            evidence_fusion/
                __init__.py
                fusion.py
                normalization.py

            reasoning/
                __init__.py
                rules.py
                probabilistic_scoring.py
                state_inference.py

            state_constructor/
                __init__.py
                affective_state.py
                cognitive_state.py
                interaction_state.py
                communication_need.py
                constructor.py

            schemas/
                __init__.py
                evidence_schema.py
                hsr_schema.py

            hsre_engine.py

        models/
            README.md

        utils/
            logging.py
            audio_utils.py
            validation.py

        tests/
            test_preprocessing.py
            test_emotion.py
            test_intent.py
            test_hsre.py
            test_api.py
```

---

## Model Summary

| Module | Selected Model/Method |
|---|---|
| Audio Preprocessing | Silero VAD + Librosa/torchaudio |
| Speech Representation | HuBERT Base |
| Speech-to-Text | Whisper Small |
| Emotion Detection | Fine-tuned HuBERT + Classifier Head |
| Intent/Semantics | BGE-M3 embeddings + similarity/classification |
| Conversation Memory | Lightweight session-based memory |
| Human State Representation | Rule-Based + Probabilistic Reasoning |
| Prompt Generation | NOT IMPLEMENTED |
| LLM | NOT IMPLEMENTED |

---

## Implementation Order

Implement strictly in this order.

1. Create project folder structure.
2. Create FastAPI health endpoint.
3. Create Express frontend.
4. Implement audio upload.
5. Implement microphone recording.
6. Implement Audio Preprocessing Unit.
7. Integrate Silero VAD.
8. Integrate HuBERT Base.
9. Integrate Whisper Small.
10. Integrate fine-tuned HuBERT emotion model.
11. Integrate BGE-M3 semantic/intent analysis.
12. Create standardized Phase 1 Evidence Object.
13. Implement Conversation Memory.
14. Create the separate HSRE module.
15. Implement Evidence Fusion.
16. Implement Rule-Based Reasoning.
17. Implement Probabilistic State Scoring.
18. Implement State Inference.
19. Implement Human State Constructor.
20. Generate final structured HSR JSON.
21. Connect FastAPI inference endpoint to Express.
22. Display structured output in the frontend.
23. Test the complete pipeline with uploaded audio.
24. Test real-time microphone input.
25. Measure latency and module-wise execution time.

---

## Main API Endpoint

**Create:** `POST /api/analyze`

**Input:** Audio file

**Output:** Structured JSON containing:
- Audio metadata
- Transcript
- Emotion analysis
- Intent analysis
- Human state representation

**Also create:** `GET /api/health`

**Response:**
```json
{
    "status": "healthy"
}
```

---

## Important Engineering Requirements

1. Keep every module independent.
2. Do not put all model logic into `main.py`.
3. Do not mix HSRE logic with emotion detection.
4. HSRE must accept structured evidence rather than raw audio.
5. Models must be loaded once during application startup, not for every request.
6. Use configuration files for model paths and HSRE weights.
7. Use typed schemas/models for API inputs and outputs.
8. Add proper error handling for invalid audio.
9. Handle unsupported audio formats gracefully.
10. Do not store user audio permanently unless explicitly required.
11. Keep inference modular so individual models can be replaced.
12. Do not use any LLM.
13. Do not add unnecessary databases, vector stores, Docker, authentication, cloud deployment, or other infrastructure unless specifically requested later.
14. Keep the first implementation local and simple.
15. The system should work with both uploaded audio and microphone-recorded audio.

---

## Final System Output

The system must **not** simply display: *"Emotion: Angry"*

It must provide a structured Human State Representation:

```json
{
    "transcript": "I have tried this several times but it is still not working.",

    "emotion": "angry",

    "emotion_confidence": 0.91,

    "intent": "requesting_help",

    "human_state": {
        "affective_state": "frustrated",

        "cognitive_state": "help_seeking",

        "interaction_state": "repeated_failure",

        "communication_need": {
            "tone": "empathetic",
            "response_style": "step_by_step",
            "detail_level": "moderate"
        }
    }
}
```

The final output is the Human State Representation. The project should demonstrate that raw human speech can be converted into structured contextual information through a modular pipeline **without using an LLM**.
