# TAED Core Package

This directory contains the core components of the Trust-Aware Explainable Defense (TAED) pipeline.

Planned organization:

- `pipeline.py`: orchestrates the complete TAED workflow
- `trust_gate.py`: computes trust-aware routing decisions
- `explanation.py`: explanation-based feature analysis
- `logic_engine.py`: final rule-based refinement

Evaluation scripts should call these components rather than containing the full pipeline implementation.
