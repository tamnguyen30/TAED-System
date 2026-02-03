import pandas as pd
import os
import re

def parse_results_file(filename):
    """Parses a results file to extract the final F1 Score from the Classification Report."""
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return None
    
    # This regex looks for the row containing 'Phishing (1)' and captures the f1-score (the 4th number).
    f1_match = re.search(r'Phishing \(1\)\s+\d+\.\d+\s+\d+\.\d+\s+(\d+\.\d+)', content)
    
    if f1_match:
        return float(f1_match.group(1))
    
    return None

def main():
    print("🚀 Starting Delta F1-Score (ΔF1) Analysis...")
    
    # List of all your models and their result file prefixes
    models = {
        'Naive Bayes': 'evaluation_results_naive_bayes.txt',
        'Logistic Regression': 'evaluation_results_logistic_regression.txt',
        'SVM (LinearSVC)': 'evaluation_results_svm.txt',
        'Random Forest': 'evaluation_results_random_forest.txt',
        'XGBoost': 'evaluation_results_xgboost.txt',
        'Shallow MLP': 'evaluation_results_mlp.txt',
        'FastText': 'evaluation_results_fasttext.txt',
        'Char-CNN': 'evaluation_results_char_cnn.txt',
        'DistilBERT': 'evaluation_results_distilbert.txt',
        'TinyBERT': 'evaluation_results_tinybert.txt',
        'MobileBERT': 'evaluation_results_mobilebert.txt'
    }
    
    # Clean F1 scores on the original (non-adversarial) test set.
    # These are taken directly from your initial training reports.
    clean_f1_mapping = {
        'Naive Bayes': 0.9255, 'Logistic Regression': 0.9895, 
        'SVM (LinearSVC)': 0.9932, 'Random Forest': 0.9926, 
        'XGBoost': 0.9895, 'Shallow MLP': 0.9925,
        'FastText': 0.8006, 'Char-CNN': 1.0000, 
        'DistilBERT': 1.0000, 'TinyBERT': 0.9994,
        'MobileBERT': 0.9944
    }
    
    results = []
    
    for model_name, filename in models.items():
        adversarial_f1 = parse_results_file(filename) 
        clean_f1 = clean_f1_mapping.get(model_name)
        
        if adversarial_f1 is not None and clean_f1 is not None:
             delta_f1 = clean_f1 - adversarial_f1
             
             results.append({
                'Model': model_name,
                'F1 Clean': f"{clean_f1:.4f}",
                'F1 Attacked': f"{adversarial_f1:.4f}",
                'Delta F1 (Degradation)': delta_f1 
            })
             
    # Create the DataFrame
    df_results = pd.DataFrame(results)
    
    # Check if DataFrame is empty before proceeding
    if df_results.empty:
        print("\nERROR: No valid F1 scores could be parsed from the files. Check filenames and content.")
        return

    # Sort by degradation (the Delta F1 column)
    df_results = df_results.sort_values(by='Delta F1 (Degradation)', ascending=False)
    
    # Format the Delta F1 column for final report display
    df_results['Delta F1 (Degradation)'] = df_results['Delta F1 (Degradation)'].apply(lambda x: f"{x:.4f}")
    
    # Print the final report
    print("\n--- Final Model Degradation Report (ΔF1) ---")
    print(" (Sorted by greatest drop in F1 Score, showing least robust models first)")
    print("-" * 65)
    print(df_results.to_markdown(index=False))
    print("\n ΔF1 analysis complete.")

if __name__ == "__main__":
    main()
