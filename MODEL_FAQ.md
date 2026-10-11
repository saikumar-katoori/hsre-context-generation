# Model and Implementation FAQ

This FAQ describes the repository as it exists. It separates active code from planned model integrations and does not invent accuracy, training, or cost results.

## What does HSRE do?

HSRE means Human State Representation Engine. It receives transcript, emotion, intent, confidence, intensity, and optional history. It fuses those signals, applies explainable rules, calculates bounded scores, infers affective/cognitive/interaction states, and returns a structured communication need. It does not generate a response and it is not a diagnosis.

## Is an LLM used?

No. The project explicitly excludes GPT, Gemini, Claude, Llama, Mistral, and other generative LLMs. Whisper is used for ASR, HuBERT-family models for speech features, and deterministic Python logic for intent fallback and HSRE reasoning. BGE-M3 is an embedding model configured for possible future use, not a text generator.

## Which models are actually configured?

- ASR: `openai/whisper-small`
- Speech representation: `facebook/hubert-base-ls960`
- Emotion: `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`
- Planned semantic embedding: `BAAI/bge-m3`

The model identifiers live in `backend/config/model_config.py`.

## Are these models trained by this project?

No. The repository loads pretrained checkpoints when the required packages, files, cache, and network access are available. It does not train or fine-tune any checkpoint. The emotion checkpoint was supplied by its model author; this project does not claim ownership of its training process.

## What happens when a model cannot load?

The adapters preserve their response shape and expose availability or fallback information. Whisper can use a deterministic demo fallback based on the audio filename. Emotion uses transcript cues and simple waveform features. HuBERT reports that an embedding is unavailable. These fallbacks keep the prototype demonstrable, but they are not substitutes for validated ML models and should be removed or made explicit in production.

## Why use Whisper Small instead of a larger Whisper model?

Whisper Small offers a useful balance between recognition quality, memory, and latency for short clips. Larger checkpoints may improve some difficult audio cases but increase model download size, RAM/VRAM use, cold-start time, and per-request compute. The adapter makes a larger or smaller checkpoint replaceable. The correct choice depends on a benchmark using the project's target audio.

## Why use HuBERT?

HuBERT is designed for speech representation rather than free-form text generation. It can provide acoustic features for downstream tasks without adding an LLM. Wav2Vec2, WavLM, or a task-specific model could be used instead if the replacement returns the same adapter contract and improves the measured target metrics.

## Why is BGE-M3 not currently producing intent?

The original design specifies BGE-M3 for semantic similarity, but the current implementation uses transparent keyword rules in `backend/language_analysis/intent_classifier.py`. This keeps the prototype lightweight and explainable. BGE-M3 can later compare a transcript embedding with predefined intent descriptions, but it should be evaluated against the current rules rather than assumed to be better.

## Which emotions are supported?

The normalized project vocabulary is `neutral`, `happy`, `sad`, `angry`, `fear`, `surprise`, `disgust`, and `frustrated`. External checkpoints may use different labels, so the adapter maps known aliases. Emotion output is an estimate from speech and text evidence, not a clinical or psychological conclusion.

## How is frustration calculated?

The current score combines emotion confidence, intent confidence, a negative-emotion tripwire, and emotion intensity. The weights are 0.45, 0.25, 0.20, and 0.10. The final value is clamped to the range 0-1. It is an engineered decision score, not a calibrated probability.

## Why not use one real-time voice model?

An end-to-end voice system can be effective, but it must coordinate streaming buffers, ASR, acoustic analysis, context, turn detection, and often generation. Large combined workloads can create GPU memory pressure, queueing, cold starts, network latency, and difficult failure isolation. They are also harder to explain. This project uses bounded short clips and separable adapters to control compute and expose intermediate evidence. It is progress-streamed, not continuous live voice inference.

## Is this the cheapest possible solution?

No implementation can promise that without a measured deployment comparison. This design is intended to be a lower-cost alternative for short-clip state extraction because HSRE itself is inexpensive CPU logic, audio length is bounded, model calls are separable, and no generated response tokens are paid for. Hosted ASR or emotion inference still costs money and local model execution still consumes CPU/GPU resources.

## What are the current input limits?

Uploads are limited to 25 MB and normalized audio is limited to 15 seconds. Browser recording stops at 15 seconds and the UI requests 10-15 seconds. These are application constraints for predictable latency and resource use, not model-theoretical limits.

## Is the system multilingual?

Whisper is multilingual, but the end-to-end implementation should currently be treated as English-oriented. Intent rules are English phrase rules, and the configured emotion checkpoint is English-oriented. A language selector, multilingual intent data, and multilingual evaluation are required before making a multilingual reliability claim.

## How accurate is it?

The repository contains no valid benchmark result. Accuracy depends on audio quality, language, model availability, fallback usage, and domain. A defensible evaluation should use speaker-independent data and report ASR WER, emotion macro-F1 and calibration, intent macro-F1, transcript availability, end-to-end latency, and failure rate.

## How should the models be fine-tuned?

For ASR, use paired audio/transcript data and report held-out word error rate. For emotion, use speaker-separated labeled clips and report macro-F1, per-class recall, confusion matrix, and calibration. For intent, label examples for every configured intent and compare rules with a classifier or embedding-similarity approach. Record dataset versions, label definitions, preprocessing, hyperparameters, and checkpoint revisions. Never tune on the test set.

## Does conversation memory work yet?

`ConversationMemory` supports adding entries, retrieving recent entries, and producing a small summary. The current inference route passes an empty history to HSRE, so repeated-failure context is scaffolded rather than fully connected to a persistent session.

## Does the API stream audio in real time?

No. `POST /api/analyze/stream` streams newline-delimited progress events while one uploaded or recorded clip is processed. It does not stream microphone frames to a continuously running inference graph.

## What should be improved before production?

Add typed request/response schemas, real VAD, temporary-file deletion, explicit unavailable states instead of filename fallbacks, memory retention controls, model/version logging, calibrated confidence, speaker-independent tests, and a benchmark against the intended real-time baseline.
