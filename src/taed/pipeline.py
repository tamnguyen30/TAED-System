"""High-level TAED pipeline interface.

This module integrates initial classification, trust estimation,
selective escalation, and final rule-based refinement.
"""

from .trust_gate import compute_trust_score, should_escalate
from .explanation import get_explanation_features
from .logic_engine import scan_for_semantic_threats


class TAEDPipeline:
    """Trust-aware phishing detection pipeline."""

    def __init__(self, classifier, escalated_model=None,
                 explainer=None, indicator_set=None,
                 threshold=0.35):
        self.classifier = classifier
        self.escalated_model = escalated_model
        self.explainer = explainer
        self.indicator_set = indicator_set or set()
        self.threshold = threshold

    def predict(self, text):
        probabilities = self.classifier.predict_proba([text])[0]
        prediction = probabilities.argmax()
        confidence = probabilities[prediction]

        features = get_explanation_features(
            text, self.explainer, self.classifier
        ) if self.explainer else []

        matched = [
            word for word in features
            if word.lower() in self.indicator_set
        ]
        fidelity = len(matched) / len(features) if features else 0.0

        trust = compute_trust_score(confidence, fidelity)

        if should_escalate(trust, self.threshold):
            if self.escalated_model:
                prediction = self.escalated_model.predict([text])[0]

            if scan_for_semantic_threats(text):
                prediction = 1

        return prediction
