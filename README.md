# TAED: Trust-Aware Explainable Defense for Phishing Detection

TAED is a hybrid phishing detection system that evaluates 
prediction trustworthiness rather than relying solely on model 
confidence. It computes a Trust Score combining three signals:

**TS = 0.35C + 0.40F − 0.25I**

- **C — Confidence:** Model certainty about its prediction
- **F — Fidelity:** Alignment of reasoning with known phishing indicators
- **I — Instability:** Explanation sensitivity to minor perturbations

Low-trust predictions are escalated through a 4-stage pipeline:
**Random Forest → Trust Gate → DistilBERT → Logic Engine**

---

## Key Results

| Metric | Value |
|--------|-------|
| TAED Attack Success Rate | 9.79% |
| Transformer Baseline ASR | up to 99.98% |
| Clean Data Accuracy | 99%+ |
| Stage 1 Latency | 28ms |
| Stage 3 Latency | 450ms |

---


## Repository Structure

```
TAED-System/
├── src/              # Core source code and training scripts
├── models/           # Trained model files
├── templates/        # Web UI
├── results/          # Evaluation outputs
├── data/             # Dataset symlinks
└── requirements.txt
```

---

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Running the System

```bash
cd TAED-System
python src/backend.py
```

Open http://localhost:5000 in your browser.

---

## Datasets

- ITASEC 2024 Phishing Corpus
- Nazario Phishing Corpus
- Apache SpamAssassin Ham Corpus
- Alhuzali et al. Synthetic Phishing Dataset (Zenodo)

---

## Reproducing Results

```bash
# Evaluate on adversarial benchmark
PYTHONPATH=. python3 src/evaluate_hybrid_v3.py

# Generate figures
PYTHONPATH=. python3 src/generate_figures.py
```