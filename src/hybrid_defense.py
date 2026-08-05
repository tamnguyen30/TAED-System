import os
import re
import numpy as np
import pandas as pd
import pickle
from urllib.parse import urlparse

try:
    from transformers import DistilBertTokenizer, TFDistilBertForSequenceClassification
    import tensorflow as tf
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class TAEDSystem:
    def __init__(self):
        print(" [TAED] Initializing Trust-Aware Explainable Defense (Ensemble Architecture)...")
        print(" Research Focus: Explanation Trustworthiness Under Adversarial Attack")
        self.alpha = 0.35
        self.beta = 0.40
        self.gamma = 0.25
        self.TS_HIGH_TRUST = 0.80
        self.TS_MEDIUM_TRUST = 0.50
        self.use_transformer = False
        self.transformer_tokenizer = None
        self.transformer_model = None
        self.rf_model = None
        self.gb_model = None
        self.phishing_evidence = {
            'spoofing': ['similar domain', 'typo', 'misspell', 'look-alike', 'impersonat'],
            'urgency': ['urgent', 'immediately', 'asap', 'limited time', 'expires', 'act now'],
            'threats': ['suspend', 'lock', 'frozen', 'terminate', 'close', 'restricted'],
            'verification': ['verify', 'confirm', 'validate', 'authenticate', 'update'],
            'financial': ['payment', 'refund', 'wire', 'bitcoin', 'gift card', 'transfer'],
            'credentials': ['password', 'username', 'login', 'credential', 'ssn'],
            'rewards': ['winner', 'prize', 'reward', 'claim', 'congratulations'],
            'authority': ['irs', 'fbi', 'bank', 'paypal', 'amazon', 'microsoft']
        }
        self.reference_phishing_features = [
            'verify', 'urgent', 'suspend', 'click', 'password', 'account',
            'update', 'confirm', 'security', 'unusual', 'locked', 'expires'
        ]
        self.suspicious_tlds = ['.gq', '.tk', '.cf', '.ml', '.ga', '.top', '.xyz', '.work', '.club', '.online']
        self.homoglyphs = {
            '@': 'a', '1': 'i', '0': 'o', '3': 'e', '$': 's', '!': 'i',
            '5': 's', '7': 't', '4': 'a', 'а': 'a', 'е': 'e', 'о': 'o',
            'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x'
        }
        self.trusted_domains = ['google.com', 'microsoft.com', 'apple.com', 'amazon.com', 'github.com', 'linkedin.com']
        self.brand_targets = ['paypal', 'amazon', 'netflix', 'microsoft', 'apple', 'google', 'facebook', 'chase']
        self._load_transformer_model()
        if not self.use_transformer:
            self._load_or_train_rf()

    def _load_transformer_model(self):
        model_dir = './models/distilbert_phishing_v3'
        if not TRANSFORMERS_AVAILABLE:
            print(" > Transformers library not available, using RF fallback")
            return
        if not os.path.isdir(model_dir):
            print(f" > DistilBERT model not found at {model_dir}, using RF fallback")
            return
        try:
            print(f" > Loading DistilBERT from {model_dir}...")
            self.transformer_tokenizer = DistilBertTokenizer.from_pretrained(model_dir)
            self.transformer_model = TFDistilBertForSequenceClassification.from_pretrained(model_dir)
            self.use_transformer = True
            print(" > DistilBERT loaded successfully! (State-of-the-art classifier active)")
        except Exception as e:
            print(f" > DistilBERT load failed: {e}")
            self.use_transformer = False

    def _load_or_train_rf(self):
        try:
            with open('taed_rf_model.pkl', 'rb') as f:
                self.rf_model = pickle.load(f)
            with open('taed_gb_model.pkl', 'rb') as f:
                self.gb_model = pickle.load(f)
            print(" > Loaded RF + GB ensemble models")
        except FileNotFoundError:
            self._train_rf()

    def _train_rf(self):
        from sklearn.pipeline import Pipeline
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        try:
            csv_file = 'data/phishing_email.csv'
            print(f" > Training ensemble on {csv_file}...")
            df = pd.read_csv(csv_file, on_bad_lines='skip')
            df = df.dropna(subset=['text_combined', 'label']).sample(n=min(len(df), 12000), random_state=42)
            X = df['text_combined'].astype(str).values
            y = df['label'].values
            print(" > Training Random Forest with TF-IDF...")
            self.rf_model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')),
                ('clf', RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=42))
            ])
            self.rf_model.fit(X, y)
            print(" > Training Gradient Boosting with TF-IDF...")
            self.gb_model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')),
                ('clf', GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42))
            ])
            self.gb_model.fit(X, y)
            with open('taed_rf_model.pkl', 'wb') as f:
                pickle.dump(self.rf_model, f)
            with open('taed_gb_model.pkl', 'wb') as f:
                pickle.dump(self.gb_model, f)
            print(" > Ensemble models saved.")
        except Exception as e:
            print(f" > Training failed: {e}")

    def _normalize_text(self, text):
        text = text.lower()
        for char, replacement in self.homoglyphs.items():
            text = text.replace(char, replacement)
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_urls(self, text):
        urls = re.findall(r'https?://\S+', text)
        urls.extend(re.findall(r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', text))
        return urls

    def _check_typosquatting(self, domain):
        domain_lower = domain.lower()
        for brand in self.brand_targets:
            if brand in domain_lower:
                if not any(trusted in domain_lower for trusted in self.trusted_domains):
                    return True
        return False

    def _analyze_urls(self, urls):
        if not urls:
            return {'has_url': 0.0, 'url_risk': 0.0, 'shortened_ratio': 0.0,
                    'typosquat_detected': False, 'ip_domain': False, 'suspicious_tld': False}
        suspicious_count = 0
        shortened_count = 0
        typosquat_detected = False
        ip_domain = False
        suspicious_tld = False
        for url in urls:
            if any(s in url.lower() for s in ['bit.ly', 'tinyurl', 'goo.gl', 'ow.ly']):
                shortened_count += 1
                suspicious_count += 1
            try:
                parsed = urlparse(url if url.startswith('http') else f'http://{url}')
                domain = parsed.netloc or parsed.path.split('/')[0]
                if any(domain.endswith(tld) for tld in self.suspicious_tlds):
                    suspicious_count += 1
                    suspicious_tld = True
                if self._check_typosquatting(domain):
                    typosquat_detected = True
                    suspicious_count += 1
                if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                    suspicious_count += 1
                    ip_domain = True
            except Exception:
                suspicious_count += 1
        return {
            'has_url': 1.0,
            'url_risk': min(suspicious_count / max(len(urls), 1), 1.0),
            'shortened_ratio': shortened_count / max(len(urls), 1),
            'typosquat_detected': typosquat_detected,
            'ip_domain': ip_domain,
            'suspicious_tld': suspicious_tld
        }

    def _calculate_semantic_density(self, text):
        normalized = self._normalize_text(text)
        total_words = len(normalized.split())
        if total_words == 0:
            return 0.0, {}
        densities = {}
        for category, keywords in self.phishing_evidence.items():
            hits = sum(1 for kw in keywords if kw in normalized)
            densities[category] = hits / total_words
        weighted_density = (
            densities.get('spoofing', 0) * 2.0 +
            densities.get('urgency', 0) * 1.5 +
            densities.get('threats', 0) * 1.8 +
            densities.get('verification', 0) * 1.3 +
            densities.get('financial', 0) * 1.6 +
            densities.get('credentials', 0) * 2.0 +
            densities.get('rewards', 0) * 1.4 +
            densities.get('authority', 0) * 1.2
        ) / 12.0
        return min(weighted_density, 1.0), densities

    def _classify_phishing_risk(self, text):
        if self.use_transformer and self.transformer_model is not None:
            enc = self.transformer_tokenizer(
                [text], truncation=True, padding=True,
                max_length=256, return_tensors='tf'
            )
            
            dataset = tf.data.Dataset.from_tensor_slices(dict(enc)).batch(1)
            preds_output = self.transformer_model.predict(dataset, verbose=0)
            logits = preds_output.logits[0]
            predicted_label = int(np.argmax(logits))
            probs = tf.nn.softmax(logits).numpy()
            return {
                'confidence': float(probs[1]),
                'ensemble_agreement': 0.0,
                'predicted_label': predicted_label
            }
        if self.rf_model is not None and self.gb_model is not None:
            X = [text]
            rf_probs = self.rf_model.predict_proba(X)[0]
            gb_probs = self.gb_model.predict_proba(X)[0]
            ensemble_probs = (rf_probs * 0.6) + (gb_probs * 0.4)
            return {
                'confidence': float(ensemble_probs[1]),
                'ensemble_agreement': float(abs(rf_probs[1] - gb_probs[1])),
                'predicted_label': int(np.argmax(ensemble_probs))
            }
        return {'confidence': 0.5, 'ensemble_agreement': 0.0, 'predicted_label': 0}

    def _generate_explanation(self, text, url_analysis, category_densities):
        components = []
        evidence = []
        if url_analysis['typosquat_detected']:
            components.append("Domain impersonation detected (typosquatting)")
            evidence.extend(['domain', 'typo', 'spoofing'])
        if url_analysis['url_risk'] >= 0.5:
            components.append(f"High-risk URL patterns (Risk: {url_analysis['url_risk']:.2f})")
            evidence.extend(['url', 'link'])
        if url_analysis['ip_domain']:
            components.append("IP address used as domain")
            evidence.append('ip')
        if url_analysis['suspicious_tld']:
            components.append("Suspicious TLD detected")
            evidence.append('domain')
        for cat, density in category_densities.items():
            if density > 0.05:
                components.append(f"{cat.title()} language detected")
                evidence.append(cat)
        if not components:
            components.append("No explicit indicators — DistilBERT detected subtle patterns." if self.use_transformer else "No significant indicators found.")
        return {
            'components': components,
            'evidence_tokens': list(set(evidence)),
            'natural_language': " | ".join(components)
        }

    def _verify_explanation_consistency(self, text, explanation, classification_result):
        score = 1.0
        issues = []
        normalized = self._normalize_text(text)
        found = sum(1 for t in explanation['evidence_tokens'] if t in normalized)
        consistency = found / max(len(explanation['evidence_tokens']), 1)
        if consistency < 0.5:
            score -= 0.2
            issues.append("Evidence weak in text")
        if classification_result['confidence'] > 0.8 and len(explanation['components']) < 2:
            score -= 0.2
            issues.append("High confidence/Low evidence")
        if classification_result['ensemble_agreement'] > 0.3:
            score -= 0.15
            issues.append("Models disagree")
        return {
            'verification_score': max(0.0, score),
            'consistency_issues': issues,
            'is_consistent': score >= 0.7
        }

    def _generate_perturbations(self, text):
        variants = []
        v1 = text
        for char, replacement in self.homoglyphs.items():
            if replacement in v1:
                v1 = v1.replace(replacement, char)
        variants.append(v1)
        words = text.split()
        if len(words) > 2:
            v2 = words.copy()
            v2[0], v2[1] = v2[1], v2[0]
            variants.append(' '.join(v2))
        chars = list(text)
        if len(chars) > 5:
            chars[2], chars[3] = chars[3], chars[2]
        variants.append(''.join(chars))
        return variants

    def analyze_email(self, text, user_feedback=None):
        urls = self._extract_urls(text)
        url_analysis = self._analyze_urls(urls)
        _, category_densities = self._calculate_semantic_density(text)
        cls_result = self._classify_phishing_risk(text)
        explanation = self._generate_explanation(text, url_analysis, category_densities)
        ver_result = self._verify_explanation_consistency(text, explanation, cls_result)

        confidence = cls_result['confidence']
        
        
        prediction = "PHISHING" if confidence >= 0.60 else "SAFE"
        C = confidence if prediction == "PHISHING" else (1.0 - confidence)

        evidence_tokens = set(explanation['evidence_tokens'])
        ref_tokens = set(self.reference_phishing_features)
        jaccard = len(evidence_tokens & ref_tokens) / len(evidence_tokens | ref_tokens) if evidence_tokens else 0.0
        fidelity = (jaccard * 0.6) + (ver_result['verification_score'] * 0.4)
        if prediction == "SAFE":
            fidelity = 1.0 - fidelity

        perturbations = self._generate_perturbations(text)
        var_scores = [abs(confidence - self._classify_phishing_risk(p)['confidence']) for p in perturbations]
        instability = float(np.mean(var_scores)) if var_scores else 0.0

        ts = (self.alpha * C) + (self.beta * fidelity) - (self.gamma * instability)
        ts = max(0.0, min(1.0, ts))

        full_explanation = explanation['natural_language']
        if not ver_result['is_consistent']:
            full_explanation += f" (Inconsistent: {', '.join(ver_result['consistency_issues'])})"
        if ts < 0.5 and prediction == "PHISHING":
            full_explanation += " [LOW TRUST: Escalate]"

        return {
            'prediction': prediction,
            'trust_score': float(ts),
            'natural_language': full_explanation,
            'explanation_components': explanation['components'],
            'consistency_issues': ver_result['consistency_issues'],
            'model_used': 'distilbert' if self.use_transformer else 'rf_gb_ensemble',
            'metrics': {
                'C (Confidence)': round(C, 2),
                'F (Fidelity)': round(fidelity, 2),
                'I (Instability)': round(instability, 2),
                'raw_features': [0] * 15
            }
        }