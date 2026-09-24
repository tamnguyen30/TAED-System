"""Evaluate the TAED trust-aware phishing detection pipeline.

This script provides the experiment entry point while core TAED components
are implemented in the taed package.
"""

import argparse
import joblib
import pandas as pd
import tqdm
from sklearn.metrics import accuracy_score, confusion_matrix
import lime.lime_text

from taed.pipeline import TAEDPipeline


DEFAULT_DATA_PATH = "data/adversarial_benchmark_dataset.csv"
RF_MODEL_PATH = "models/random_forest_pipeline.joblib"
BERT_MODEL_PATH = "models/distilbert_phishing_v2"


def main():
    parser = argparse.ArgumentParser(description="Evaluate TAED pipeline")
    parser.add_argument("--data", default=DEFAULT_DATA_PATH)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    texts = df["attacked_text"].fillna("").astype(str).tolist()
    labels = df["original_label"].tolist()

    rf_model = joblib.load(RF_MODEL_PATH)
    explainer = lime.lime_text.LimeTextExplainer(
        class_names=["Safe", "Phishing"]
    )

    # Optional escalation model can be loaded here.
    pipeline = TAEDPipeline(
        classifier=rf_model,
        explainer=explainer
    )

    predictions = []
    for text in tqdm.tqdm(texts):
        predictions.append(pipeline.predict(text))

    print(f"TAED Accuracy: {accuracy_score(labels, predictions):.4f}")

    tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()
    print("Confusion Matrix:")
    print(f"TN: {tn}\nFP: {fp}\nFN: {fn}\nTP: {tp}")


if __name__ == "__main__":
    main()
