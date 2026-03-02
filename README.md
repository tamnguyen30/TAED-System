
# TAED: Trust-Aware Explainable Defense

Phishing detection system using explainability-based trust metrics for adversarial robustness.

## Paper
Under review (USENIX Security 2026)

## Overview
TAED combines model confidence, explanation fidelity, and explanation stability into a Trust Score metric to detect adversarial phishing attacks that fool traditional ML classifiers.

## Requirements
- Python 3.9+
- Node.js 18+
- scikit-learn, LIME, transformers
- See `requirements.txt` and `package.json` for full dependencies

## Quick Start

### Command Line Interface
```bash
# launch the demo server (Flask/FastAPI)
python backend.py
```

### Full Quick‑Start Workflow

1. **Data preparation (clean the noisy CSV, fix header leakage)**

```bash
# use your venv's python or invoke via ./ if the file is executable
python3 process_data.py            # creates data/unified_phishing_dataset.csv
python3 balance_data.py            # writes data/balanced_phishing_dataset.csv
python3 split_data.py              # outputs train/test splits under data/splits/
# or, after chmod +x, you can run directly:
# ./process_data.py && ./balance_data.py && ./split_data.py
```

2. **Model training**

- Transformer (DistilBERT) – recommended for production:
  ```bash
  python train_distilbert.py    # reads splits and saves model at models/distilbert_phishing_model
  ```
- Classic TF‑IDF ensemble (RF+GB) is trained automatically by `backend.py` or
  `hybrid_defense` when transformer files are absent.

3. **Run the server or use `hybrid_defense` programatically**

The code will prefer a loaded DistilBERT model if
`models/distilbert_phishing_model` exists, otherwise it falls back to the
traditional ensemble.  Re‑clean your data and re‑train whenever the corpus
changes to avoid the “garbage pattern” issue you described.
