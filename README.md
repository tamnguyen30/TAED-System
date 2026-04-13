## Overview

TAED is a hybrid phishing detection system that goes beyond model confidence to evaluate *why* a prediction was made. It computes a Trust Score combining three signals:

**TS = 0.3C + 0.4F − 0.3I**

- **C — Confidence:** How certain is the model?
- **F — Fidelity:** Is the model reasoning about the right features?
- **I — Instability:** Does a small change flip the explanation?

Low-trust predictions are escalated through a 4-stage pipeline:
**Random Forest → Trust Gate → DistilBERT → Rule Engine**

---

## Key Results

| Metric | Value |
|--------|-------|
| TAED Attack Success Rate | 7.89% |
| MobileBERT Attack Success Rate | 59.06% |
| Clean Data Accuracy | 99.3% |
| Stage 1 Latency | 28ms |

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

## Setup

```bash
git clone https://github.com/tamnguyen30/TAED-System
cd TAED-System
pip install -r requirements.txt
```

---

## Running the Demo

```bash
python src/backend.py
```

Open http://localhost:5000 in your browser.

---

## Datasets

- Phishing Email Dataset (Alam/Kaggle)
- Enron Email Dataset
- Phishing Curated (Zenodo 8339691)
