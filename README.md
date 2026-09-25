# TAED: Trust-Aware Explainable Defense for Phishing Detection

This repository contains the implementation and evaluation pipeline for TAED, a trust-aware phishing detection framework that combines initial classification, explanation-based trust estimation, and selective escalation.

## Artifact Overview

The artifact includes:

- TAED pipeline components
- Trust-aware routing through the Trust Gate
- Explanation-based analysis modules
- Adversarial evaluation procedures
- Reproduction documentation and experiment configuration

## Repository Structure

```
TAED-System/
├── src/
│   ├── taed/              # Core TAED pipeline components
│   ├── evaluation/        # Evaluation scripts
│   ├── preprocessing/     # Dataset preparation utilities
│   └── visualization/    # Figure generation tools
├── attacks/               # Adversarial transformation procedures
├── experiments/           # Evaluation workflows
├── results/               # Experimental outputs
├── models/                # Model artifact information
├── data/                  # Dataset documentation
├── docs/                  # Additional documentation
├── requirements.txt
└── README.md
```

## TAED Pipeline

TAED follows a four-stage workflow:

1. Initial phishing classification using the baseline model.
2. Trust assessment using prediction confidence, explanation alignment, and instability signals.
3. Selective escalation of low-trust samples for additional analysis.
4. Rule-based verification for final decision refinement.

The Trust Score is computed as:

```
TS = clip(0.35*C + 0.40*F - 0.25*I, 0, 1)
```

where:

- **C** represents prediction confidence.
- **F** represents explanation–dictionary alignment from LIME-selected features.
- **I** represents prediction instability under perturbation probes.

## Reproduction Workflow

1. Prepare datasets according to the documentation in `data/`.
2. Configure required model components.
3. Run evaluation scripts in `experiments/`.
4. Generate metrics and analysis outputs.

## Dataset Availability

The artifact does not redistribute third-party datasets. Dataset sources, preprocessing procedures, and configuration details are documented to support reconstruction of the experimental setup.

## Model Artifacts

Large trained model files are not included directly. Required model configurations and artifact information are documented separately.

## Citation

This repository accompanies the submitted manuscript. Citation information will be added after publication.
