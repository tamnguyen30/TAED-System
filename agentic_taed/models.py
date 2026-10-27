"""Adapter that invokes the unmodified repository TAEDPipeline with real RF weights."""
from pathlib import Path
import hashlib
import sys
import time
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


class SeededExplainer:
    def __init__(self, samples=256):
        self.samples = samples
        self.features = []

    def explain_instance(self, text, predict_fn, num_features):
        from lime.lime_text import LimeTextExplainer
        seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
        explainer = LimeTextExplainer(class_names=['safe', 'phishing'], random_state=seed)
        exp = explainer.explain_instance(text, predict_fn, num_features=num_features,
                                         num_samples=self.samples)
        self.features = [feature for feature, _ in exp.as_list()]
        return exp


class TransformerAdapter:
    def __init__(self, path):
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True).eval()

    def predict(self, texts):
        with self.torch.no_grad():
            tokens = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors='pt')
            return self.model(**tokens).logits.argmax(dim=-1).cpu().numpy()


class RepositoryTAED:
    def __init__(self, rf_path=None, transformer_path=None, lime_samples=256, require_deep=False):
        import joblib
        import sklearn
        from taed.pipeline import TAEDPipeline
        from phishing_indicators import PHISHING_INDICATORS
        self.path = Path(rf_path or ROOT / 'models/random_forest_pipeline.joblib')
        if not self.path.is_file():
            raise FileNotFoundError(f'Required trained model missing: {self.path}')
        with warnings.catch_warnings(record=True) as caught:
            self.classifier = joblib.load(self.path)
        self.load_warnings = [str(w.message) for w in caught]
        if list(self.classifier.classes_) != [0, 1]:
            raise ValueError('Repository core assumes probability indices equal labels [0,1].')
        self.explainer = SeededExplainer(lime_samples)
        deep = TransformerAdapter(transformer_path) if transformer_path else None
        if require_deep and deep is None:
            raise FileNotFoundError('Full four-stage TAED requires the original DistilBERT checkpoint.')
        self.pipeline = TAEDPipeline(self.classifier, escalated_model=deep,
                                     explainer=self.explainer, indicator_set=PHISHING_INDICATORS)
        self.metadata = {'backend': 'repository_TAEDPipeline', 'trained_model': str(self.path.relative_to(ROOT)) if self.path.is_relative_to(ROOT) else self.path.name,
                         'sha256': hashlib.sha256(self.path.read_bytes()).hexdigest(),
                         'sklearn': sklearn.__version__, 'deep_model_available': deep is not None,
                         'mode': 'full' if deep else 'partial_RF_LIME_rules_NO_DistilBERT',
                         'alpha': .30, 'beta': .40, 'gamma': .25, 'instability': .05,
                         'threshold': .35, 'lime_features': 3, 'lime_samples': lime_samples,
                         'warnings': self.load_warnings}

    def predict(self, text):
        from taed.trust_gate import compute_trust_score
        from phishing_indicators import PHISHING_INDICATORS
        start = time.perf_counter()
        self.explainer.features = []
        label = int(self.pipeline.predict(text))
        probabilities = self.classifier.predict_proba([text])[0]
        features = self.explainer.features
        fidelity = sum(w.lower() in PHISHING_INDICATORS for w in features) / len(features) if features else 0.
        trust = compute_trust_score(float(max(probabilities)), fidelity)
        return {'malicious': label == 1, 'label': label, 'rf_phishing_probability': float(probabilities[1]),
                'features': features, 'explanation_available': bool(features), 'fidelity': fidelity,
                'trust_score': trust, 'escalated': trust < self.pipeline.threshold,
                'deep_model_available': self.metadata['deep_model_available'],
                'latency_ms': (time.perf_counter()-start)*1000}
