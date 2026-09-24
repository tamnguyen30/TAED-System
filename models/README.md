# Model inventory

Tracked files: `random_forest_pipeline.joblib`, `logistic_regression_pipeline.joblib`, `naive_bayes_pipeline.joblib`, `svm_pipeline.joblib`, and `xgboost_pipeline.joblib`.

DistilBERT checkpoints referenced by the Python scripts are not included in this checkout. Training versions, model hashes, and source-data split membership should accompany an experiment release. Filenames alone do not identify training provenance or demonstrate compatibility with the current environment.
# Model Artifacts

This directory contains trained model artifacts used by TAED experiments.

## Organization

- Classical models: baseline classifiers used for comparison.
- Trust-aware components: models used within the TAED routing pipeline.

Large model files are not included in the artifact repository. Instructions for obtaining required models and reproducing experiments are provided in the main README.

## Reproducibility

Model configurations, training procedures, and evaluation scripts are documented in the repository to support reproduction of reported results.
