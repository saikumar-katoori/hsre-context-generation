# Project Run Results

These are operational smoke-check results from the current repository state, not research benchmark results.

| Check | Result | Evidence / notes |
|---|---|---|
| Backend tests | PASS: 3 passed | `backend/.venv` Python; run from `backend/` with `python -m pytest tests/test_api.py -q`. One Starlette/httpx deprecation warning. |
| Frontend production build | PASS | Vite 5.4.21; build completed in 2.37 s. Output: 31 modules transformed; JS 148.12 kB (47.85 kB gzip), CSS 5.04 kB (1.74 kB gzip). |
| Backend health endpoint | PASS: HTTP 200, `{"status":"healthy"}` | `GET http://127.0.0.1:8000/api/health`. |
| Frontend startup | PASS | React app loaded at `http://127.0.0.1:3000/`; page title: `HSRE Context Generation`. |
| Frontend screenshot | Captured | [fig4_frontend_upload.png](images/fig4_frontend_upload.png); real initial upload screen, no inference result shown. |
| End-to-end audio inference | NOT RUN | No valid local audio input was available. The current files in `backend/tmp_audio/` are 0-8 bytes and cannot serve as audio recordings. |
| Emotion / intent accuracy | NOT MEASURED | No labeled evaluation set, predictions, or ground-truth labels are present. |
| Per-module / end-to-end latency | NOT MEASURED | No valid clip was analyzed and no timing measurements were captured. Do not populate Table VIII from build or health-check timings. |
| Ablation, robustness, fairness | NOT EVALUATED | No reference annotations or experimental protocols/results are present. |

The frontend and backend development servers are currently running at the URLs above. The backend tests verify health/root routes and a narrow fallback emotion behavior; they do not validate ASR, model quality, or the paper's claimed benchmark results.