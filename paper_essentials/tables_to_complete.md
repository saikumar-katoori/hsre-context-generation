# Experimental Data to Complete

Use this worksheet to populate the paper's empty tables and author TODOs. Keep raw records, split definitions, model/checkpoint revisions, and analysis scripts alongside the final results so every reported value can be reproduced. Use `Not evaluated` rather than an estimate when a measurement has not been run.

## Table III: Dataset statistics

Report the dataset name/version, inclusion criteria, speaker-independent split method, and counts after preprocessing. Do not count files in `backend/tmp_audio/` as a dataset without labels, consent/usage rights, and a documented protocol.

| Split | Utterances | Speakers | Emotion classes (counts or list) |
|---|---:|---:|---|
| Train | TBD | TBD | TBD |
| Validation | TBD | TBD | TBD |
| Test | TBD | TBD | TBD |

Additional record: dataset/corpus and version: TBD; language(s): TBD; labeling protocol and annotator agreement: TBD; speaker-disjoint split: TBD; exclusions/corrupt audio: TBD.

## Table IV: Emotion classifier training configuration

The checked-in project has no classifier fine-tuning pipeline. The currently configured emotion checkpoint is a wav2vec2 XLSR model, not a fine-tuned HuBERT head in this repository. Fill this table only after documenting the actual model and training run.

| Hyperparameter | Value |
|---|---|
| Base encoder/checkpoint | TBD |
| Classification head | TBD |
| Optimizer | TBD |
| Learning rate / schedule | TBD |
| Batch size | TBD |
| Epochs / stopping rule | TBD |
| Train / validation / test split | TBD |
| Random seeds | TBD |
| Class balancing / augmentation | TBD |
| Best-checkpoint selection metric | TBD |

## Table V: Emotion recognition performance

Evaluate all systems on the same held-out split and label mapping. Include exact checkpoint and test protocol; literature numbers from other datasets are not directly comparable.

| Model | WA (%) | UA (%) | Macro-F1 |
|---|---:|---:|---:|
| Proposed emotion model | TBD | TBD | TBD |
| Baseline 1 (name/checkpoint) | TBD | TBD | TBD |
| Baseline 2 (name/checkpoint) | TBD | TBD | TBD |

Evaluation set/version: TBD; number of test utterances: TBD; confidence intervals or repeated-run variation: TBD.

## Table VI: Intent classification performance

The current classifier is keyword-based, not BGE-M3 similarity-based. State which implementation is being evaluated and use a labeled test set with an explicit unknown class policy.

| Intent class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| asking_information | TBD | TBD | TBD | TBD |
| requesting_help | TBD | TBD | TBD | TBD |
| complaint | TBD | TBD | TBD | TBD |
| confirmation | TBD | TBD | TBD | TBD |
| disagreement | TBD | TBD | TBD | TBD |
| feedback | TBD | TBD | TBD | TBD |
| greeting | TBD | TBD | TBD | TBD |
| farewell | TBD | TBD | TBD | TBD |
| troubleshooting | TBD | TBD | TBD | TBD |
| unknown | TBD | TBD | TBD | TBD |
| Macro average | TBD | TBD | TBD | TBD |

## Table VII: HSRE case studies

Collect examples from an approved, documented source. Include the ground-truth annotation and the system output in the analysis notes even if the paper table stays compact. Cover the interaction categories named in the paper and explain rule/scorer disagreements.

| Transcript excerpt (de-identified) | Reference emotion/state | Predicted emotion | Predicted intent | Inferred communication need | Rule/scorer disagreement |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | TBD | TBD | TBD | TBD | TBD |

Include 6-10 additional cases beyond the paper's running example if following its TODO. A synthetic or manually authored example can illustrate behavior, but must be labeled as illustrative, not empirical.

## Table VIII: Latency and real-time performance

Measure end-to-end latency from endpoint receipt to response, and each stage with a consistent timer. Record hardware, software versions, concurrency, audio duration, warm/cold model state, number of repetitions, and mean plus variability (preferably median and p95 as well). The current response's `input.duration` is hard-coded to zero and must not be used as a duration measurement.

| Module | Mean latency (ms) | SD (ms) | Median (ms) | p95 (ms) | % of total |
|---|---:|---:|---:|---:|---:|
| Audio preprocessing | TBD | TBD | TBD | TBD | TBD |
| Speech representation (HuBERT adapter) | TBD | TBD | TBD | TBD | TBD |
| Speech-to-text | TBD | TBD | TBD | TBD | TBD |
| Emotion inference | TBD | TBD | TBD | TBD | TBD |
| Intent inference | TBD | TBD | TBD | TBD | TBD |
| HSRE (fusion + reasoning + construction) | TBD | TBD | TBD | TBD | TBD |
| Total end-to-end | TBD | TBD | TBD | TBD | 100 |

Hardware (CPU/GPU and RAM): TBD; OS/runtime versions: TBD; clip duration range: TBD; repetitions: TBD; model cold-start included?: TBD; concurrency: TBD.

## HSRE ablation (paper TODO)

Define identical inputs and scoring criteria for each configuration. The repository does not currently provide isolated rule-only and scorer-only evaluation modes or reference labels.

| Configuration | Affective agreement | Cognitive agreement | Interaction agreement | Communication-need agreement | Overall metric / CI |
|---|---:|---:|---:|---:|---|
| Rules only | TBD | TBD | TBD | TBD | TBD |
| Scoring only | TBD | TBD | TBD | TBD | TBD |
| Combined | TBD | TBD | TBD | TBD | TBD |

## Robustness and fairness (paper TODOs)

| Analysis | Required data / result |
|---|---|
| Accent / language | Cohort definition, sample counts, emotion/intent metrics by cohort, uncertainty: TBD |
| Gender / age, where available and appropriate | Consent, cohort definition, sample counts, metrics and uncertainty: TBD |
| Noise / microphone / speaking-rate conditions | Controlled condition definitions, sample counts, degradation from clean reference: TBD |
| Multi-speaker / long-session memory | Protocol, speaker attribution method, session length, outcomes: TBD |
| Limitations and consent | Dataset permissions, consent/disclosure, retention policy, known coverage gaps: TBD |

Do not infer demographic attributes from voices for this table. Report only appropriately collected and consented metadata, or state that subgroup evaluation was not performed.