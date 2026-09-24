# Reproduction Guide

This document describes the steps required to reproduce the experiments reported in the TAED paper.

## 1. Environment Setup

Install required dependencies:

```bash
pip install -r requirements.txt
```

## 2. Dataset Preparation

Obtain the required public datasets from their original sources and follow the preprocessing instructions in `data/README.md`.

## 3. Model Training

Train baseline and TAED components using the provided training scripts and configurations.

## 4. Evaluation

Run evaluation scripts to reproduce:

- clean-data performance
- adversarial robustness evaluation
- trust-aware routing experiments

## 5. Results

Generated tables and figures should be saved under the results directory.

