# TAED: Trust-Aware Explainable Defense for Phishing Detection

This repository contains the implementation and evaluation pipeline for TAED, a trust-aware phishing detection framework that combines classification, explanation-based trust estimation, and selective escalation.

## Overview

TAED addresses a key limitation of traditional phishing detectors: high prediction confidence does not always indicate reliable decisions under adversarial manipulation.

The framework follows a four-stage pipeline:

1. Initial phishing classification
2. Trust Gate evaluation
3. Deep model escalation for uncertain cases
4. Logic-based decision refinement

## Repository Structure

```
TAED-System/
├── src/                  # Core implementation
├── attacks/              # Adversarial attack generation and benchmarks
├── results/              # Experimental outputs and figures
├── models/               # Trained model artifacts (not included)
├── data/                 # Dataset instructions
├── templates/            # Optional interface components
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Reproducibility

The artifact includes preprocessing, model evaluation, attack generation, and analysis scripts required to reproduce the reported experiments.

Example:

```bash
PYTHONPATH=. python3 src/evaluate_hybrid_v3.py
```

## Dataset Availability

Experiments use publicly available phishing and benign email datasets, including:

- ITASEC Phishing Email Corpus
- Nazario Phishing Corpus
- Apache SpamAssassin Public Corpus
- Public synthetic phishing datasets

Dataset download instructions and preprocessing details are provided separately.

## Citation

If you use this repository, please cite the associated TAED paper.
