# Reproduction guide

## What is included

Five statistical checkpoints are tracked: Random Forest, logistic regression, naive Bayes, SVM, and XGBoost. Historical scripts and outputs are included. Checkpoints are serialized Python objects: load only trusted artifacts in an isolated environment matching their training dependencies.

## What is missing

This checkout does not include `data/`, the exact benchmark CSV, split files, or the DistilBERT directories referenced by the evaluators. Therefore a fresh clone cannot currently reproduce the full pipeline's reported results. The old CCS appendix's statement that `data/adversarial/` contains the full benchmark does not describe this checkout.

| Workflow | Required input paths |
| --- | --- |
| RF training | `data/splits/X_train.csv`, `y_train.csv`, `X_test.csv`, `y_test.csv` |
| Attack generation | `data/splits/X_test_ccs.csv`, `data/splits/y_test_ccs.csv` |
| Historical cascade | `models/random_forest_pipeline.joblib`, `models/distilbert_phishing_v2/`, a CSV with `attacked_text` and `original_label` |
| Heuristic v3 evaluator | `models/random_forest_pipeline.joblib`, `data/adversarial/adversarial_benchmark_dataset_ccs_clean.csv` (or an explicit CSV path) |
| Flask demo | `models/distilbert_phishing_v3/`, or root-level RF/GB pickle files; may attempt training from `data/phishing_email.csv` |

Dataset sources named in the manuscript include ITASEC 2024, Nazario, SpamAssassin, and the synthetic phishing corpus. Public source availability does not substitute for the precise versions, filtering, split membership, and attack-generation outputs needed to reproduce an experiment.

## Conditional commands

Run from the repository root, after supplying the corresponding assets and compatible dependencies. These are historical entry points, not promises of reproducing the revised paper:

```bash
python3 scripts/check_artifact.py
python3 src/train_random_forest.py
PYTHONPATH=. python3 src/generate_adversarial_dataset.py
python3 src/evaluate_hybrid_system.py --data /path/to/benchmark.csv
python3 src/evaluate_hybrid_v3.py /path/to/benchmark.csv
```

Training and generation can overwrite outputs. Use a separate experiment checkout and preserve the original checkpoint and dataset hashes. The attack generator targets 20,000 rows and can download a T5 model; it does not reconstruct the exact 16,836-row benchmark from metadata alone.

## Dependencies

`requirements.txt` is historical and not a tested lockfile. Imports in additional workflows require `lime`, `joblib`, `matplotlib`, `torch`, `xgboost`, and `sentencepiece` as applicable. TensorFlow-based Transformers scripts also need a compatible TensorFlow/Keras/Transformers combination. Record versions from the environment that produced each result rather than assuming current versions reproduce it.

## Metric definitions

- Accuracy: correct final labels / all evaluated rows.
- Overall error rate: incorrect final labels / all evaluated rows.
- Phishing evasion rate: phishing rows labeled legitimate / evaluated phishing rows.
- Conditional ASR, if used: successful evasions / attacks on originally correctly detected phishing inputs; record the conditioning explicitly.
- ADR at the gate: escalated adversarial rows / adversarial rows.
- FER: escalated clean rows / clean rows; this is not final false-positive rate.

Store confusion counts and denominators alongside percentages. Mixed-label error rate is not interchangeable with phishing evasion rate. Record the number of unique source messages separately from transformed rows.

## Completing the release

Attach the selected implementation, environment lock, checkpoint hashes, dataset identifiers and licenses, exact source-message split membership, attack parameters and seeds, and machine-readable evaluation outputs. Keep transformed versions of a source email in its assigned partition. Map each manuscript table/figure to a command and output file. Document any unavailable assets and redistribution restrictions rather than substituting a new run for an old result.
