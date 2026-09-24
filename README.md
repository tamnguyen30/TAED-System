# TAED: Trust-Aware Explainable Defense for Phishing Detection

Research code for phishing classification, adversarial text transformations, and trust-guided routing.

## Start here

- [Implementation map](docs/IMPLEMENTATIONS.md): choose an entry point and understand its behavior.
- [Reproduction guide](docs/REPRODUCIBILITY.md): required data, checkpoints, commands, and metric definitions.
- [Anonymous review guide](docs/ANONYMOUS_REVIEW.md): prepare a separate review snapshot.
- [Historical results](results/README.md): distinguish stored outputs from new evaluations.

## Artifact status

This checkout contains multiple research and demonstration variants. It is not yet a complete reproduction package for the revised ACNS manuscript: the benchmark data, exact splits, and DistilBERT checkpoints are not included. Some historical scripts are incomplete. Run the offline inventory below before selecting an experiment.

```bash
python3 scripts/check_artifact.py
```

This command uses only the Python standard library, does not load models or download data, and exits nonzero when required artifacts or Python syntax are missing. It does not validate model performance.

## Method described in the revised manuscript

The reference routing score is `clip(0.35*C + 0.40*F - 0.25*I, 0, 1)`, with escalation when `TS < 0.50`:
This repository contains the implementation and evaluation pipeline for TAED, a trust-aware phishing detection framework that combines initial classification, explanation-based trust estimation, and selective escalation.

## Overview

TAED addresses a key challenge in phishing detection: a confident prediction may still be unreliable under adversarial manipulation. Instead of relying only on the final classifier output, TAED estimates prediction trustworthiness and routes uncertain samples for additional analysis.

The framework follows a four-stage pipeline:

1. Initial phishing classification
2. Trust-aware routing through the Trust Gate
3. Deep model escalation for low-trust predictions
4. Logic-based decision refinement

## Repository Structure

```
TAED-System/
├── src/
│   ├── taed/              # Core TAED pipeline components
│   ├── evaluation/        # Evaluation scripts
│   ├── preprocessing/     # Dataset preparation
│   └── visualization/    # Figure generation
├── attacks/               # Adversarial attack generation and benchmarks
├── experiments/           # Reproduction workflows
├── results/               # Experimental outputs
├── models/                # Model artifact instructions
├── data/                  # Dataset instructions
├── docs/                  # Artifact documentation
├── requirements.txt
└── README.md
```

## Installation

- **C:** probability assigned by the initial Random Forest to its predicted class.
- **F:** fraction of up to five LIME-selected tokens in the 30-term indicator dictionary (alignment, not explanation fidelity).
- **I:** mean absolute change in RF phishing probability under the specified probes.

High-trust messages retain the RF label. Escalated messages receive a DistilBERT prediction followed by deterministic rules. A rule match yields phishing; otherwise the DistilBERT label is retained.

This paragraph describes the manuscript specification. Existing implementations differ; consult the implementation map before attributing a result to this configuration. The grid-search reference `(0.5, 0.1, 0.4)` is a separate configuration.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/` | Training, evaluation, analysis, and historical Flask demonstration scripts |
| `attacks/` | Character, URL, paraphrasing, noise, and instruction-insertion transformations |
| `models/` | Five tracked statistical-model joblib files; see the model inventory |
| `templates/index.html` | Flask demonstration page |
| `templates/web-app/` | Separate React/Express prototype and Python bridge variants |
| `results/` | Historical logs, figures, and summaries |
| `docs/` | Reproduction and implementation documentation |
| `scripts/` | Dependency-free artifact readiness check |

## Environment and execution

Use an isolated Python environment. `requirements.txt` contains historical lower bounds, not a validated environment lock. It also omits some imports used by optional scripts; see the reproduction guide before installing or running a workflow.

The historical Flask demo starts with `python src/backend.py` from the repository root after its dependencies and artifacts are supplied. It can attempt training on startup and fall back to a different model. It is not the reference four-stage evaluation.

For the separate web prototype, see `templates/web-app/package.json` and the implementation map. Its backend is Express, not Flask. Neither demo should be presented as reproducing the revised benchmark solely because its interface displays a Trust Score.

## Results and availability

Recorded results remain unchanged under `results/`. The former README's single headline ASR mixed documentation with historical outputs and has been replaced by provenance guidance. No experiments were rerun as part of this repository cleanup.

The public repository's owner, history, and links identify its authors. Use a separately reviewed anonymous snapshot for double-anonymous review; see the anonymous review guide.
## Reproducing Experiments

The artifact workflow is:

1. Prepare datasets using the instructions in `data/`.
2. Configure required models.
3. Run evaluation scripts in `experiments/`.
4. Generate results and figures using the provided analysis tools.

Additional reproduction details are available in `docs/`.

## Dataset Availability

Experiments use publicly available phishing and benign email datasets. Dataset sources, preprocessing procedures, and construction details are documented in the artifact documentation.

Raw datasets are not redistributed when their licenses or original sources restrict redistribution.

## Model Artifacts

Large trained model files are not stored in the repository. Instructions for obtaining required models and configuring experiments are provided separately.

## Citation

Please cite the associated TAED publication when using this artifact.
