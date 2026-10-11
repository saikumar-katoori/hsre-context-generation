# Paper Essentials

This folder contains a code-checked implementation audit, a worksheet for the paper's missing experimental data, and reusable figure assets. It does not contain fabricated benchmark results.

## Before submitting the paper

The manuscript currently describes several planned capabilities as implemented. Reconcile these points with the repository before describing the work as an evaluated real-time system:

| Paper claim | Checked implementation | Action for the paper |
|---|---|---|
| Express.js frontend with microphone recording | The frontend is React + Vite and currently offers audio-file upload. `/api/recording` is a placeholder, not a recording client. | Correct the stack and describe upload-only interaction, or implement and test recording first. |
| Whisper Small, HuBERT Base, and a fine-tuned HuBERT emotion head | Whisper Small and HuBERT Base identifiers are configured. The emotion checkpoint is `ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition`; no training code or fine-tuning results are present. Deterministic fallbacks are used when models are unavailable. | Name the actual checkpoint and fallback behavior; do not call the emotion model fine-tuned unless training evidence is added. |
| Silero VAD and BGE-M3 are active | Silero VAD is not called. BGE-M3 is configured but not loaded by intent inference; intent uses keyword rules. | Mark both as planned/not used, or implement and evaluate them. |
| Conversation memory enriches each analysis | A memory helper exists, but the analysis route passes `conversation_history: []` on every request. | Describe the current single-request behavior; do not claim context-aware multi-turn results. |
| Models load once at application startup | Whisper pipeline and HuBERT components are loaded from inference functions; there is no common startup model-loading lifecycle. Emotion model loading is cached after first attempt. | Remove the startup claim or add startup loading and measure cold/warm behavior. |
| HSRE uses normalized emotion probabilities, linguistic and contextual evidence | Fusion preserves probability values, but the scorer uses emotion confidence, intensity, and intent confidence. The current route supplies no history. The configured context/linguistic weights multiply a derived negative-emotion term and emotion intensity, respectively. | Document the exact heuristic and avoid implying calibrated probabilities or active contextual evidence. |
| Complete audio metadata and non-persistent audio | The analysis response currently reports a hard-coded input duration of `0.0`; preprocessing writes source and normalized files under `backend/tmp_audio/` and does not remove them. | Fix metadata and cleanup/retention behavior, or report these limitations accurately. |
| Typed API schemas and specified error behavior | The analysis route returns dictionaries rather than declared request/response models. It handles several upload errors, but duration depends on successful audio decoding. | Add/describe schema validation and enumerate error cases accurately. |
| No LLM or prompt generation | No generative model is called by the backend. The frontend does construct a copyable “LLM handoff” prompt. | Clarify that inference is non-generative but the UI includes an optional prompt handoff; reconcile the “Prompt Generation: Not implemented” row. |
| Results, real-time latency, ablation, robustness, and fairness findings | No labeled evaluation dataset, training run, metrics report, ablation, subgroup analysis, or latency report is checked in. `backend/tmp_audio/` is scratch input, not a documented labeled benchmark. | Fill the worksheet only from reproducible experiments. Until then, label results as not evaluated and remove numerical performance claims. |

The example values repeated in the paper (for example emotion confidence `0.91` and intent confidence `0.87`) are illustrative unless they can be tied to a logged, reproducible evaluation record. Do not enter them as measured results by default.

## Figure assets

- `images/fig1_implemented_pipeline.svg` is a diagram of the checked-in implementation, including fallback and currently inactive components. It is not a diagram of the paper's intended architecture. Use it only if the manuscript is revised to describe the implementation.
- `images/fig3_confusion_matrix_template.svg` is an empty layout. Replace it with a normalized confusion matrix generated from held-out test predictions.
- `images/fig5_latency_template.svg` is an empty layout. Replace it with measured per-module latency data; it intentionally contains no bars or values.
- `images/fig4_frontend_upload.png` is a genuine screenshot of the running frontend in its initial upload-only state. It does not show an analysis result, so it is not a substitute for the paper's requested result screenshot.
- The live checks and their limits are recorded in [run_results.md](run_results.md). No usable audio sample was available for a real inference screenshot; remove filenames or identifying information from any future capture before publication.

## Verification scope

This audit checks manuscript implementation claims against the repository's code and documentation. It does not independently validate the cited research bibliography or reproduce the referenced papers' findings.