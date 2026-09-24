# TAED: Trust-Aware Explainable Defense for Phishing Detection

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

```bash
pip install -r requirements.txt
```

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
