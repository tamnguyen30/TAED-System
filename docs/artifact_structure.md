# Artifact Structure

The repository is organized to separate the TAED implementation, evaluation scripts, and supporting resources.

## Core Implementation

`src/taed/` contains the Trust-Aware Explainable Defense pipeline:

- `pipeline.py`: integrates classification, trust estimation, escalation, and final decision logic.
- `trust_gate.py`: computes trust scores and routing decisions.
- `explanation.py`: explanation-based feature extraction.
- `logic_engine.py`: rule-based verification stage.

## Evaluation

Evaluation scripts should call the TAED modules rather than duplicate pipeline logic.

## Reproduction Workflow

1. Prepare datasets.
2. Load trained models.
3. Run evaluation scripts.
4. Generate metrics and figures reported in the paper.
