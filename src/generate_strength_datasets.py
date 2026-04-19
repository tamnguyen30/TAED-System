import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import accuracy_score

MODELS = {
    'Random Forest': 'models/random_forest_pipeline.joblib',
    'Naive Bayes': 'models/naive_bayes_pipeline.joblib',
    'SVM': 'models/svm_pipeline.joblib',
    'Logistic Regression': 'models/logistic_regression_pipeline.joblib',
    'XGBoost': 'models/xgboost_pipeline.joblib',
}

DATASETS = {
    '10%': 'data/adversarial/adversarial_strength_10pct_ccs.csv',
    '30%': 'data/adversarial/adversarial_strength_30pct_ccs.csv',
    '50%': 'data/adversarial/adversarial_strength_50pct_ccs.csv',
}

def evaluate(model, df):
    X = df['attacked_text'].fillna('').astype(str)
    y_true = df['original_label']
    y_pred = model.predict(X)
    acc = accuracy_score(y_true, y_pred)
    phishing = df[df['original_label'] == 1]
    y_pred_phishing = model.predict(phishing['attacked_text'].fillna('').astype(str))
    fooled = (y_pred_phishing == 0).sum()
    asr = fooled / len(phishing) if len(phishing) > 0 else 0
    return acc, asr

def main():
    print("Loading datasets...")
    datasets = {name: pd.read_csv(path) for name, path in DATASETS.items()}

    print("Loading models...")
    models = {name: joblib.load(path) for name, path in MODELS.items()}

    results = []
    for model_name, model in models.items():
        for strength, df in datasets.items():
            acc, asr = evaluate(model, df)
            results.append({
                'model': model_name,
                'strength': strength,
                'accuracy': acc,
                'asr': asr
            })
            print(f"{model_name} @ {strength}: Acc={acc:.4f} ASR={asr:.4f}")

    # Print summary table
    print("\n" + "="*70)
    print("ATTACK STRENGTH ANALYSIS — ASR BY MODEL AND STRENGTH")
    print("="*70)
    print(f"{'Model':<25} {'10% ASR':>10} {'30% ASR':>10} {'50% ASR':>10}")
    print("-"*55)

    for model_name in MODELS.keys():
        row = [r for r in results if r['model'] == model_name]
        asr_10 = next(r['asr'] for r in row if r['strength'] == '10%')
        asr_30 = next(r['asr'] for r in row if r['strength'] == '30%')
        asr_50 = next(r['asr'] for r in row if r['strength'] == '50%')
        print(f"{model_name:<25} {asr_10:>10.4f} {asr_30:>10.4f} {asr_50:>10.4f}")

    # Save results
    df_results = pd.DataFrame(results)
    df_results.to_csv('results/attack_strength_analysis.csv', index=False)
    print("\nSaved to results/attack_strength_analysis.csv")

if __name__ == "__main__":
    main()